# SEB compatibility plan

Status: **research draft — compatibility is not yet claimed**

SafeExamOS should be explicit about what "SEB compatible" means.

## Compatibility levels

### L0 — configuration reader

Can inspect a `.seb` configuration and explain supported/unsupported settings. Does not start an exam.

### L1 — basic exam launch

Supports:

- start URL;
- browser enablement;
- basic navigation restrictions;
- basic URL filtering;
- browser profile lifecycle.

### L2 — practical configuration compatibility

Adds:

- certificates;
- proxies;
- uploads/downloads;
- additional windows/resources;
- keyboard/mouse policy mapping;
- display/device policy mapping;
- config-purpose/session semantics.

### L3 — SEB Server interoperability

Adds validated behavior for:

- connecting to SEB Server;
- exam discovery/selection;
- receiving server-provided configuration;
- connectivity/session reporting.

### L4 — assessment-system key interoperability

Only after independent validation:

- Config Key-compatible request behavior;
- Browser Exam Key-compatible request behavior;
- version/platform semantics;
- test vectors agreed with upstream or validated against reference clients.

SafeExamOS must not advertise L4 before this is proven.

## Current upstream observations

Current SEB Windows source shows that browser requests may include:

- `X-SafeExamBrowser-ConfigKeyHash`
- `X-SafeExamBrowser-RequestHash`

The values are calculated from configuration/key material and the request URL.

Upstream release notes explicitly state that Browser Exam Key is platform-specific, including different values for 32-bit and 64-bit Windows builds of the same version. This is a major compatibility constraint for SafeExamOS.

## Configuration areas already identified upstream

From the current Windows configuration-key implementation:

- applications: permitted/prohibited processes, signatures;
- browser: start URL, downloads/uploads, PDF behavior, toolbar, popup policy;
- URL filtering;
- proxy configuration;
- certificates;
- display policy;
- keyboard/mouse restrictions;
- proctoring;
- security settings;
- server settings.

Many of these are operating-system-specific in implementation even when the key name is shared.

## Mapping policy

Every key SafeExamOS encounters must be classified:

| Classification | Meaning |
|---|---|
| supported | implemented with equivalent intended behavior |
| translated | implemented with a Linux-specific mechanism judged equivalent |
| ignored-safe | irrelevant and safe to ignore, documented |
| warning | exam can start but semantics differ |
| blocking | security-sensitive and unsupported; exam must not start |
| unknown | unrecognized; default handling depends on security classification |

Security-sensitive unknown keys should default to **blocking** until reviewed.

## Example mapping

| SEB concept | SafeExamOS direction |
|---|---|
| `startURL` | Chromium initial navigation |
| URL filter | SafeExamOS browser request policy |
| permitted Windows executable | unsupported/translated only if a Linux equivalent is explicitly configured |
| prohibited Windows process | not directly portable; OS image should not contain arbitrary applications |
| keyboard shortcuts | compositor/input policy |
| display count | DRM/Wayland output policy |
| embedded certificates | isolated trust store for exam session |
| proxy | browser/system network policy |
| screen proctoring | compatible research target, not assumed identical |

## SEB Server observations

Current Windows flow:

1. initialize server settings;
2. connect;
3. retrieve available exams;
4. select an exam;
5. obtain a configuration resource;
6. load the configuration;
7. notify the server of the selected exam;
8. obtain additional session/key information;
9. start connectivity/monitoring.

This gives us a useful interoperability model, but protocol details and version compatibility still need dedicated research and tests.

## Test strategy

Create a corpus of configurations with one feature changed at a time.

For each:

- expected Windows/macOS behavior where documented;
- SafeExamOS interpretation;
- browser/network observable behavior;
- security result;
- compatibility classification.

Do not use production exams for compatibility testing.

## Upstream sources

- https://github.com/SafeExamBrowser/seb-win-refactoring
- https://github.com/SafeExamBrowser/seb-server
- https://safeexambrowser.org/
- Windows request header implementation:
  https://github.com/SafeExamBrowser/seb-win-refactoring/blob/master/SafeExamBrowser.Browser/Handlers/ResourceHandler.cs
- Windows configuration keys:
  https://github.com/SafeExamBrowser/seb-win-refactoring/blob/master/SafeExamBrowser.Configuration/ConfigurationData/Keys.cs
