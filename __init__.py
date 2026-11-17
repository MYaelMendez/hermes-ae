"""hermes-ae 2.2.0 — one receipted tool for the Asimov robot studio.

`ae` dispatches to the registered tools of all local plugins by loading their
modules with a lightweight FakeCtx, then writes a single HUMAN://ROOT
hash-chained receipt for every action. No heavy imports at registration.
"""
import json, hashlib, importlib.util, subprocess, os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / 'scripts'
HERMES_HOME = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes'))
PY = os.environ.get('HERMES_AE_PYTHON', '/usr/local/bin/python3')
PLUGINS = Path(os.environ.get('HERMES_AE_PLUGINS', HERMES_HOME / 'plugins'))
LEDGER = Path(os.environ.get('HERMES_AE_LEDGER', HERMES_HOME / 'ae-receipts.jsonl'))

# op -> (plugin, tool). Use op="call" with plugin/tool for anything else.
SHORTCUTS = {
    'speak':        ('tiny-voca-voice', 'tts_speak'),
    'voices':       ('tiny-voca-voice', 'tts_voices'),
    'render':       ('ffmpeg-agentic', 'ffmpeg_render'),
    'probe':        ('ffmpeg-agentic', 'ffmpeg_probe'),
    'gallery':      ('ffmpeg-agentic', 'video_gallery'),
    'witness':      ('ffmpeg-agentic', 'ffmpeg_witness'),
    'vlc':          ('vlc-mesh', 'vlc_media'),
    'nodes':        ('vlc-mesh', 'vlc_nodes'),
    'vlc_receipts': ('vlc-mesh', 'vlc_receipts'),
    'robot_say':    ('hermes-asimov', 'asimov_say'),
    'robot_status': ('hermes-asimov', 'asimov_status'),
    'robot_video':  ('hermes-asimov', 'asimov_voice_video'),
    'studio_video': ('hermes-asimov', 'asimov_studio_video'),
    'studio':       ('mujoco-studio', 'studio_shoot'),
    'physics':      ('mujoco-studio', 'studio_physics'),
    'studio_status':('mujoco-studio', 'studio_status'),
    'studio_sync':  ('mujoco-studio', 'studio_sync'),
    'studio_publish':('mujoco-studio', 'studio_publish'),
    'robot_voice':  ('robotVOICE', 'robot_speak'),
    'face_states':  ('robotVOICE', 'robot_face_states'),
    'chimera_speak':('chimera-voice', 'chimera_speak'),
    'chimera_sing': ('chimera-voice', 'chimera_sing'),
    'ae_command':   ('ae-c2', 'ae_command'),
    'ae_status':    ('ae-c2', 'ae_status'),
}

_cache = {}

# Bundled orchestrators — run in-process scripts, not legacy plugins.
LOCAL_OPS = {
    'studio_video': ('studio_video.py', 1500),
    'free_walk': ('free_walk_video.py', 1500),
}


def _run_local(script, args, timeout):
    path = SCRIPTS / script
    if not path.exists():
        return {'success': False, 'error': f'bundled script missing: {path}'}
    try:
        p = subprocess.run([PY, str(path), json.dumps(args)], capture_output=True,
                           text=True, timeout=timeout)
        if p.returncode != 0:
            return {'success': False, 'error': (p.stderr or p.stdout)[-1000:]}
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception as e:
        return {'success': False, 'error': f'{type(e).__name__}: {e}'}


def _out(d):
    return json.dumps(d, ensure_ascii=False)


def _last_hash():
    if not LEDGER.exists():
        return 'GENESIS'
    lines = [x for x in LEDGER.read_text(encoding='utf-8').splitlines() if x.strip()]
    if not lines:
        return 'GENESIS'
    try:
        return json.loads(lines[-1])['hash']
    except Exception:
        return 'GENESIS'


def _receipt(action, detail):
    e = {'ts': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
         'action': action, 'authority': 'HUMAN://ROOT', 'prev': _last_hash(),
         'detail': detail}
    payload = json.dumps(e, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    e['hash'] = hashlib.sha256(payload.encode()).hexdigest()
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open('a', encoding='utf-8') as f:
        f.write(json.dumps(e, ensure_ascii=False) + '\n')
    return e


def _verify_chain():
    if not LEDGER.exists():
        return {'success': True, 'count': 0, 'head': 'GENESIS'}
    lines = [x for x in LEDGER.read_text(encoding='utf-8').splitlines() if x.strip()]
    prev, ok, broken = 'GENESIS', True, None
    for i, line in enumerate(lines):
        e = json.loads(line)
        h = e.pop('hash', None)
        if e.get('prev') != prev:
            ok, broken = False, i; break
        payload = json.dumps(e, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        calc = hashlib.sha256(payload.encode()).hexdigest()
        if calc != h:
            ok, broken = False, i; break
        prev = h
    return {'success': ok, 'count': len(lines), 'head': prev, 'broken_at': broken}


class FakeCtx:
    def __init__(self):
        self.tools = {}
        self.commands = {}
        self.hooks = {}

    def register_tool(self, name, toolset, handler, schema):
        self.tools[name] = (handler, toolset)

    def register_command(self, name, handler, description, args_hint):
        self.commands[name] = (handler, description, args_hint)

    def register_skill(self, name, path):
        pass

    def register_hook(self, name, handler):
        self.hooks[name] = handler


def _tools(plugin):
    if plugin in _cache:
        return _cache[plugin]
    path = PLUGINS / plugin / '__init__.py'
    if not path.exists():
        return {}
    spec = importlib.util.spec_from_file_location(f'ae_{plugin}', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    ctx = FakeCtx()
    if hasattr(m, 'register'):
        m.register(ctx)
    _cache[plugin] = ctx.tools
    return ctx.tools


def _call(plugin, tool, args):
    tools = _tools(plugin)
    if tool not in tools:
        return {'success': False, 'error': f'tool {tool!r} not in plugin {plugin!r}',
                'available': sorted(tools)}
    handler = tools[tool][0]
    try:
        r = handler(args)
        if isinstance(r, str):
            try:
                r = json.loads(r)
            except Exception:
                pass
        return r
    except Exception as e:
        return {'success': False, 'error': f'{type(e).__name__}: {e}'}


def register(ctx):
    def ae(args: dict) -> str:
        op = args.get('op', 'status')
        arg = dict(args)
        arg.pop('op', None)

        if op == 'status':
            dirs = sorted(p.name for p in PLUGINS.iterdir() if p.is_dir()) if PLUGINS.exists() else []
            chain = _verify_chain()
            result = {'success': True, 'actor': 'hermes-ae', 'authority': 'HUMAN://ROOT',
                      'version': '2.2.0', 'plugins_on_disk': len(dirs),
                      'shortcuts': sorted(SHORTCUTS), 'receipts': chain}
        elif op == 'receipts':
            limit = int(arg.get('limit') or 10)
            lines = LEDGER.read_text(encoding='utf-8').splitlines() if LEDGER.exists() else []
            result = {'success': True, 'count': len(lines),
                      'receipts': [json.loads(x) for x in lines[-limit:]]}
        elif op == 'verify':
            result = _verify_chain()
        elif op == 'ops':
            result = {'success': True, 'shortcuts': sorted(SHORTCUTS), 'local_ops': sorted(LOCAL_OPS),
                      'note': 'use op=free_walk or studio_video for bundled pipelines; op=call reaches local legacy plugins'}
        elif op == 'call':
            plugin, tool = arg.pop('plugin', None), arg.pop('tool', None)
            if not plugin or not tool:
                result = {'success': False, 'error': 'plugin and tool are required for op=call'}
            else:
                result = _call(plugin, tool, arg)
        elif op in LOCAL_OPS:
            script, timeout = LOCAL_OPS[op]
            result = _run_local(script, arg, timeout)
        elif op in SHORTCUTS:
            plugin, tool = SHORTCUTS[op]
            result = _call(plugin, tool, arg)
        else:
            result = {'success': False, 'error': f'unknown op {op!r}',
                      'available': ['status', 'receipts', 'verify', 'ops', 'call'] + sorted(LOCAL_OPS) + sorted(SHORTCUTS)}

        try:
            ok = bool(result.get('success', True))
        except Exception:
            ok = False
        rec = _receipt(f'AE://{op.upper()}', {'ok': ok})
        out = {'success': ok, 'op': op, 'result': result, 'receipt': rec}
        return _out(out)

    ctx.register_tool(
        name='ae', toolset='hermes-ae', handler=ae,
        schema={'type': 'object', 'properties': {
            'op': {'type': 'string', 'description': 'Operation: status, receipts, verify, ops, call, or any shortcut.'},
            'plugin': {'type': 'string', 'description': 'Plugin name for op=call.'},
            'tool': {'type': 'string', 'description': 'Tool name for op=call.'},
            'text': {'type': 'string'}, 'voice': {'type': 'string'},
            'output': {'type': 'string'}, 'script': {'type': 'string'},
            'preset': {'type': 'string'}, 'camera': {'type': 'string'},
            'scene': {'type': 'string'}, 'steps': {'type': 'integer'},
            'limit': {'type': 'integer'}, 'arg': {'type': 'string'},
            'node': {'type': 'string'}, 'action': {'type': 'string'},
            'seconds': {'type': 'integer'}, 'captions': {'type': 'boolean'},
            'physics': {'type': 'boolean'}, 'publish': {'type': 'boolean'},
        }, 'required': []},
    )
