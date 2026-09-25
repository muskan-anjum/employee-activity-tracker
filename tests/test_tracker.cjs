const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function tracker(initialState = { session_id: 1, status: 'Working' }) {
    let now = 1000000;
    let state = initialState;
    const handlers = {};
    const timers = new Map();
    const writes = [];
    const elements = {};
    const context = {
        Date: { now: () => now },
        document: {
            addEventListener: (name, fn) => { handlers[name] = fn; },
            getElementById: id => elements[id] ||= {},
            querySelector: () => ({ content: 'test-csrf' }),
        },
        navigator: {},
        window: { addEventListener: (name, fn) => { handlers[name] = fn; } },
        setInterval: (fn, delay) => timers.set(delay, fn),
        fetch: async (url, options) => {
            if (url.endsWith('/state')) return { ok: true, json: async () => state };
            writes.push(JSON.parse(options.body));
            return { ok: true };
        },
    };
    vm.runInNewContext(fs.readFileSync('static/activity_tracker.js', 'utf8'), context);
    return {
        advance: seconds => { now += seconds * 1000; timers.get(1000)(); },
        input: name => handlers[name](),
        sync: async next => { state = next; await timers.get(5000)(); },
        flush: () => context.window.workaiTracker.flush(), writes,
    };
}
const settle = () => new Promise(resolve => setImmediate(resolve));

test('tracker sends counts only and transitions from active to idle', async () => {
    const t = tracker(); await settle();
    t.input('keydown'); t.input('mousemove');
    t.advance(30); await t.flush();
    assert.deepEqual(t.writes[0], { active_seconds: 30, idle_seconds: 0, keyboard_events: 1, mouse_events: 1, session_id: 1 });
    t.advance(40); await t.flush();
    assert.equal(t.writes[1].active_seconds, 30);
    assert.equal(t.writes[1].idle_seconds, 10);
});

test('breaks and stopped sessions do not produce telemetry', async () => {
    const t = tracker({ session_id: 1, status: 'On Break' }); await settle();
    t.input('keydown'); t.advance(30); await t.flush();
    assert.equal(t.writes.length, 0);
    await t.sync({ session_id: 1, status: 'Working' });
    t.input('click'); t.advance(10); await t.flush();
    assert.equal(t.writes.length, 1);
    assert.equal(t.writes[0].keyboard_events, 0);
    await t.sync({ session_id: null, status: 'Stopped' });
    t.advance(30); await t.flush();
    assert.equal(t.writes.length, 1);
});

test('changing work sessions discards the old session pending interval', async () => {
    const t = tracker(); await settle();
    t.input('keydown'); t.advance(10);
    await t.sync({ session_id: 2, status: 'Working' });
    t.input('click'); t.advance(5); await t.flush();
    assert.equal(t.writes[0].session_id, 2);
    assert.equal(t.writes[0].keyboard_events, 0);
    assert.equal(t.writes[0].active_seconds, 5);
});
