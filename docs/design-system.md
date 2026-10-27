# SafeExamOS design system

Status: **mandatory project rule**

SafeExamOS user interfaces must visually follow the current Safe Exam Browser design language unless an upstream-compatible UI element is impossible or harms accessibility.

This is not a vague inspiration rule. UI work must be checked against upstream SEB references and documented.

## Sources of truth

Primary references:

1. current SEB Windows UI source;
2. current SEB website;
3. current SEB macOS/iOS UI where cross-platform behavior matters;
4. accessibility guidance and VPAT information.

Initial upstream references:

- `SafeExamBrowser.UserInterface.Desktop/Templates/Colors.xaml`
- `SafeExamBrowser.UserInterface.Desktop/Templates/Buttons.xaml`
- `SafeExamBrowser.UserInterface.Desktop/Windows/Taskbar.xaml`
- `SafeExamBrowser.UserInterface.Desktop/Windows/RuntimeWindow.xaml`
- `SafeExamBrowser.UserInterface.Desktop/Windows/SplashScreen.xaml`
- https://safeexambrowser.org/

## Baseline tokens extracted from current SEB Windows

| Token | Upstream value | SafeExamOS use |
|---|---:|---|
| background | `#F0F0F0` | taskbars, utility surfaces |
| transparent background | `rgba(240,240,240,.93)` equivalent | overlays where appropriate |
| emphasis background | `rgba(211,211,211,.60)` equivalent | selected/hover utility surfaces |
| primary text | `#000000` | normal text |
| secondary text | `DimGray` | secondary status text |
| focus/accent border | `DodgerBlue` | focus, selected controls, progress |
| hover fill | `LightBlue` / translucent light blue | hover states |
| pressed border | `SkyBlue` | active state |
| main panel | `#FFFFFF` | dialog/pre-flight surfaces |
| error/log surface | black/white in upstream log UI | diagnostic-only views |

### Typography

Upstream Windows installer explicitly uses **Segoe UI**. SafeExamOS should use:

```css
font-family: "Segoe UI", "Noto Sans", "Liberation Sans", sans-serif;
```

On Linux, Segoe UI must not be redistributed without appropriate rights. Noto Sans is the preferred open fallback.

### Geometry

Current SEB Windows UI is intentionally utilitarian:

- square or very lightly rounded controls;
- thin 1 px accent borders;
- restrained shadows (normally none);
- compact spacing;
- clear status/progress UI;
- no glassmorphism;
- no decorative gradients;
- no oversized consumer-app cards;
- no animated background decoration.

SafeExamOS must not drift into a generic modern dashboard aesthetic.

## Interaction rules

### Buttons

Default:

- neutral/transparent background;
- 1 px transparent or neutral border;
- black text.

Hover:

- LightBlue-like fill;
- DodgerBlue border.

Pressed:

- SkyBlue-like border;
- slightly stronger border emphasis.

Disabled:

- reduced opacity.

### Focus

Every keyboard-focusable control must have a visible focus state. Prefer the SEB blue accent and never remove the browser/toolkit focus indicator without replacing it.

### Status

Use explicit text plus color/icon. Never encode readiness only with color.

Examples:

- `Ready`
- `Network unavailable`
- `Unsupported configuration`
- `Exam mode active`

## SafeExamOS screens

### Pre-flight

Should resemble a native SEB configuration/runtime utility, not a separate branded product.

Structure:

- white or #F0F0F0 surface;
- compact title/header;
- thin blue border/accent;
- straightforward form rows;
- status list;
- primary action at bottom right.

### Exam launcher

Minimal choices:

- exam code;
- URL;
- local `.seb` file;
- network/accessibility controls.

No app-store-style tiles.

### Exam taskbar

Follow current SEB taskbar behavior and proportions where possible:

- compact height;
- #F0F0F0 background;
- applications left;
- notifications/system controls right;
- clock;
- quit control if policy permits.

### Locked/error state

High-contrast, unmistakable, and structurally similar to SEB lock/error flows. Security errors must not be styled like casual notifications.

## Website direction

The official SEB website currently uses a restrained Bootstrap-derived visual language with:

- white background;
- dark text;
- blue links/accent (`#337ab7` family);
- conventional documentation/navigation hierarchy.

Project documentation pages, future admin web UI, and public-facing SafeExamOS pages should stay visually adjacent to that style rather than introducing unrelated branding.

## Branding and trademark boundary

Visual consistency does **not** mean impersonation.

Until permission/affiliation exists:

- do not claim SafeExamOS is an official SEB product;
- keep the independent-project disclaimer visible in public-facing material;
- do not redistribute SEB logos/assets unless their license/permission has been verified;
- use our own SafeExamOS name even when adopting compatible layout/colors.

## UI review checklist

Every UI PR must document:

- upstream SEB screen/component used as reference;
- changed visual tokens;
- keyboard-only behavior;
- screen-size/resolution behavior;
- accessibility implications;
- screenshots or recordings;
- reason for any intentional divergence.

A UI PR that introduces an unrelated design language should not be merged.
