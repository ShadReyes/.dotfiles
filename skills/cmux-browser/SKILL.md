---
name: cmux-browser
description: "User-invocable only: /cmux-browser. Reference for cmux browser automation CLI commands."
---

# CMUX Browser Automation

Automate embedded browser surfaces in cmux via the `cmux browser` CLI.

## Surface Targeting

Most commands require a target surface. Pass it positionally or via `--surface`:

```bash
cmux browser surface:1 snapshot
cmux browser --surface surface:2 navigate https://example.com
```

To discover available surfaces:

```bash
cmux browser identify
```

## Command Reference

### Navigation

```bash
cmux browser open <url>                          # Open URL in new surface
cmux browser open-split <url>                    # Open URL in split
cmux browser <surface> navigate <url>            # Navigate existing surface
cmux browser <surface> back                      # Go back
cmux browser <surface> forward                   # Go forward
cmux browser <surface> reload                    # Reload page
cmux browser <surface> url                       # Get current URL
```

All navigation commands support `--snapshot-after` to capture page state after the action.

### Waiting

Block until a condition is met:

```bash
cmux browser <surface> wait --load-state complete --timeout-ms 15000
cmux browser <surface> wait --selector "#checkout" --timeout-ms 10000
cmux browser <surface> wait --text "Order confirmed"
cmux browser <surface> wait --url-contains "/dashboard"
cmux browser <surface> wait --function "window.__appReady === true"
```

Flags: `--selector`, `--text`, `--url-contains`, `--load-state <interactive|complete>`, `--function <js>`, `--timeout-ms <ms>`, `--timeout <seconds>`

### DOM Interaction

All mutating actions support `--snapshot-after`:

```bash
cmux browser <surface> click "<selector>"
cmux browser <surface> dblclick "<selector>"
cmux browser <surface> hover "<selector>"
cmux browser <surface> focus "<selector>"
cmux browser <surface> check "<selector>"
cmux browser <surface> uncheck "<selector>"
cmux browser <surface> scroll-into-view "<selector>"
cmux browser <surface> type "<selector>" --text "hello"
cmux browser <surface> fill "<selector>" --text "user@example.com"
cmux browser <surface> press "Enter"
cmux browser <surface> keydown "Shift"
cmux browser <surface> keyup "Shift"
cmux browser <surface> select "<selector>" --value "option1"
cmux browser <surface> scroll --selector "<selector>" --dx 0 --dy 300
```

Selectors and text can be passed positionally or via `--selector`/`--text` flags.

### Inspection

```bash
cmux browser <surface> snapshot                          # Full accessibility tree
cmux browser <surface> snapshot --interactive --compact   # Compact interactive-only
cmux browser <surface> snapshot --selector "#main"        # Scoped snapshot
cmux browser <surface> screenshot --out /tmp/page.png     # Screenshot to file
cmux browser <surface> get text "h1"                      # Get element text
cmux browser <surface> get html "#content"                # Get element HTML
cmux browser <surface> get value "input#email"            # Get input value
cmux browser <surface> get attr "#link" --attr href       # Get attribute
cmux browser <surface> get count ".item"                  # Count elements
cmux browser <surface> get title                          # Page title
cmux browser <surface> get url                            # Current URL
cmux browser <surface> get box "#element"                 # Bounding box
cmux browser <surface> get styles "#element"              # Computed styles
cmux browser <surface> is visible "#modal"                # Visibility check
cmux browser <surface> is enabled "#submit"               # Enabled check
cmux browser <surface> is checked "#agree"                # Checked check
cmux browser <surface> find role button --name "Submit"   # Find by ARIA role
cmux browser <surface> find text "Welcome"                # Find by text
cmux browser <surface> find testid "login-form"           # Find by test ID
cmux browser <surface> find first --selector ".card"      # First match
cmux browser <surface> find nth --index 2 --selector "li" # Nth match
cmux browser <surface> highlight "#element"               # Highlight element
```

### JavaScript & Injection

```bash
cmux browser <surface> eval "document.title"
cmux browser <surface> eval --script "return document.querySelectorAll('a').length"
cmux browser <surface> addinitscript "window.__injected = true"    # Runs on every navigation
cmux browser <surface> addscript "console.log('loaded')"           # Run once
cmux browser <surface> addstyle "body { background: red; }"        # Inject CSS
```

### Frames

```bash
cmux browser <surface> frame main                        # Switch to main frame
cmux browser <surface> frame selector --selector "iframe#app"  # Switch to iframe
```

### Dialogs

```bash
cmux browser <surface> dialog accept "OK"
cmux browser <surface> dialog dismiss
```

### Downloads

```bash
cmux browser <surface> download wait --path /tmp --timeout-ms 30000
```

### Cookies & Storage

```bash
cmux browser <surface> cookies get --name session
cmux browser <surface> cookies set --name token --value abc123 --domain example.com
cmux browser <surface> cookies clear --all
cmux browser <surface> storage local get --key myKey
cmux browser <surface> storage local set --key myKey --value "data"
cmux browser <surface> storage session clear
```

### State Persistence

```bash
cmux browser <surface> state save /tmp/session.json
cmux browser <surface> state load /tmp/session.json
```

### Tabs

```bash
cmux browser <surface> tab list
cmux browser <surface> tab new https://example.com
cmux browser <surface> tab switch 2
cmux browser <surface> tab close
```

### Console & Errors

```bash
cmux browser <surface> console list
cmux browser <surface> console clear
cmux browser <surface> errors list
cmux browser <surface> errors clear
```

### Viewport & Emulation

```bash
cmux browser <surface> viewport 1280 720
cmux browser <surface> geolocation 37.7749 -122.4194
cmux browser <surface> offline true
```

### Network

```bash
cmux browser <surface> network route "**/*.png" --abort       # Block images
cmux browser <surface> network route "/api/*" --body '{"ok":true}'  # Mock API
cmux browser <surface> network unroute "**/*.png"
cmux browser <surface> network requests
```

### Tracing & Screencast

```bash
cmux browser <surface> trace start /tmp/trace.zip
cmux browser <surface> trace stop
cmux browser <surface> screencast start
cmux browser <surface> screencast stop
```

## Common Workflows

### Navigate and Verify

```bash
cmux browser surface:1 navigate https://example.com --snapshot-after
cmux browser surface:1 wait --load-state complete --timeout-ms 10000
cmux browser surface:1 snapshot --interactive --compact
```

### Fill and Submit a Form

```bash
cmux browser surface:1 fill "#email" --text "user@example.com" --snapshot-after
cmux browser surface:1 fill "#password" --text "secret"
cmux browser surface:1 click "button[type='submit']" --snapshot-after
cmux browser surface:1 wait --text "Welcome" --timeout-ms 10000
```

### Debug a Page

```bash
cmux browser surface:1 errors list
cmux browser surface:1 console list
cmux browser surface:1 screenshot --out /tmp/debug.png
cmux browser surface:1 snapshot --interactive
```

### Save and Restore Session

```bash
cmux browser surface:1 state save /tmp/session.json
# ... later ...
cmux browser surface:1 state load /tmp/session.json
```

## Tips

- Use `--snapshot-after` on mutating actions to immediately verify the result without a separate `snapshot` call.
- Use `snapshot --interactive --compact` for a concise view of actionable elements.
- Use `wait` before inspecting to ensure the page is ready.
- Use `screenshot` when visual verification is needed (e.g., layout issues).
- Selectors follow standard CSS selector syntax.
- The `find` subcommand uses Playwright-style locators (role, text, testid, etc.).
