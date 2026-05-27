---
name: remote-dom
description: Use when implementing, architecting, or troubleshooting sandboxed UI rendering with Shopify's @remote-dom packages. Use when synchronizing DOM elements between isolated environments (iframes, web workers) and a host application, defining custom elements for cross-environment communication, or building plugin/extension systems with controlled UI rendering.
---

# Shopify Remote DOM

## Overview

Remote DOM synchronizes a tree of DOM elements from a sandboxed JavaScript environment (iframe/worker) to a host application's real DOM. It replaces the older `remote-ui` library with native DOM APIs instead of abstract component representations.

**Core principle:** Define custom elements in the remote environment, observe mutations, serialize changes as JSON messages, and reconstruct the tree on the host side.

## When to Use

- Building extension/plugin systems where third-party code renders controlled UI
- Moving UI computation to web workers (off main thread)
- Rendering from sandboxed iframes into a parent page
- Creating Shopify UI Extensions (checkout, admin, POS)
- Any architecture needing isolated UI rendering with host-controlled components

**When NOT to use:**
- Simple iframe embedding (use `<iframe>` directly)
- Same-origin, same-thread rendering (use React/framework directly)
- Server-side rendering without client interactivity

## Architecture

```
Remote Environment (sandbox)         Host Environment (main thread)
├─ RemoteElement definitions         ├─ RemoteReceiver / DOMRemoteReceiver
├─ RemoteMutationObserver            ├─ Component map (tag → host component)
├─ Shadow DOM tree                   ├─ Actual rendered DOM
└─ Serializes mutations → JSON ───── └─ Deserializes → applies to real DOM
         ↑                                        │
         └──────── Events (JSON) ←────────────────┘
```

**Communication channels:** `postMessage` (iframe) or `MessageChannel` (worker).

## Packages

| Package | Purpose |
|---------|---------|
| `@remote-dom/core` | RemoteElement, RemoteMutationObserver, RemoteReceiver, DOMRemoteReceiver |
| `@remote-dom/polyfill` | DOM API polyfill for web workers (Window, Document, Element, Event) |
| `@remote-dom/react` | `createRemoteComponent()`, `RemoteRootRenderer` for React host/remote |
| `@remote-dom/preact` | Preact equivalents of React integration |
| `@remote-dom/signals` | Fine-grained signal-based reactive updates |

## Quick Reference

### Defining Remote Elements

```typescript
import {RemoteElement} from '@remote-dom/core';

class MyButton extends RemoteElement {
  static remoteProperties = {
    label: {type: String, attribute: true},
    disabled: {type: Boolean, attribute: true},
    onPress: {event: true},  // maps to 'press' event
  };

  static remoteMethods = ['focus'];
}

customElements.define('my-button', MyButton);
```

### Property Type Mapping

| Type | Attribute behavior | Notes |
|------|-------------------|-------|
| `String` | Pass-through | Default type |
| `Boolean` | Presence = true, absence = false | String `"false"` is truthy! |
| `Number` | Parsed from string | NaN if invalid |
| `{event: true}` | Registers event listener | `onPress` → `press` event |

**`attribute: true`** — sync from HTML attribute (attribute is source of truth)
**No `attribute`** — JavaScript property is source of truth (not reflected to attribute)

### Remote Side Setup

**In iframe (native DOM):**
```typescript
import {RemoteMutationObserver} from '@remote-dom/core';

const observer = new RemoteMutationObserver(connection);
observer.observe(document.body);

// Now any DOM mutations on document.body are serialized and sent
const button = document.createElement('my-button');
button.setAttribute('label', 'Click me');
document.body.appendChild(button);
```

**In web worker (polyfilled DOM):**
```typescript
import '@remote-dom/polyfill';
import {RemoteRootElement} from '@remote-dom/core';

// RemoteRootElement auto-connects to host
const root = new RemoteRootElement();
document.body.appendChild(root);
```

### Host Side Setup

**DOM-based (simplest):**
```typescript
import {DOMRemoteReceiver} from '@remote-dom/core';

const receiver = new DOMRemoteReceiver();
receiver.connect(document.getElementById('host-container'));
// Remote elements are mirrored as matching custom elements in host DOM
```

**React-based:**
```typescript
import {RemoteReceiver} from '@remote-dom/core';
import {RemoteRootRenderer} from '@remote-dom/react';

const receiver = new RemoteReceiver();

function App() {
  return (
    <RemoteRootRenderer
      receiver={receiver}
      components={new Map([
        ['my-button', MyButtonHostComponent],
      ])}
    />
  );
}
```

### React Integration (Remote Side)

```typescript
import {createRemoteComponent} from '@remote-dom/react';

// Wraps custom element for use as React component in remote env
const Button = createRemoteComponent('my-button', MyButtonElement);

function RemoteApp() {
  return (
    <Button label="Click me" onPress={() => console.log('pressed')}>
      <span>Child content</span>
    </Button>
  );
}
```

### Communication Wiring

**iframe → host:**
```typescript
// Host
const iframe = document.getElementById('sandbox');
const receiver = new DOMRemoteReceiver();
receiver.connect(hostContainer);

iframe.contentWindow.postMessage({type: 'init'}, '*');
window.addEventListener('message', (event) => {
  receiver.receive(event.data);
});

// Remote (inside iframe)
const connection = {
  send(message) { window.parent.postMessage(message, '*'); }
};
```

**Worker → host:**
```typescript
// Host
const worker = new Worker('remote.js');
const receiver = new DOMRemoteReceiver();
receiver.connect(hostContainer);

worker.addEventListener('message', (event) => {
  receiver.receive(event.data);
});

// Remote (inside worker)
const connection = {
  send(message) { self.postMessage(message); }
};
```

## Event Naming Convention

| Property | Event name | Notes |
|----------|-----------|-------|
| `onPress` | `press` | Strip `on`, lowercase |
| `onClick` | `click` | Standard DOM event |
| `onClickMe` | `click-me` | camelCase → kebab-case |
| `{event: 'custom'}` | `custom` | Explicit override |

## Common Mistakes

**1. Reading DOM measurements synchronously**
Remote DOM is async. `offsetHeight`, `getBoundingClientRect()`, etc. are unavailable in the remote environment. Use remote methods or host-side measurement callbacks.

**2. Mutating undeclared properties**
Only properties in `remoteProperties` are synchronized. Setting other properties does nothing across the bridge.

**3. Boolean attribute coercion**
`<my-button disabled="false">` — `disabled` is `true` because the attribute is present. Remove the attribute entirely for `false`.

**4. Object property mutations**
Mutating an object property in-place won't trigger synchronization. Replace the entire object: `el.config = {...el.config, key: newValue}`.

**5. Forgetting to batch updates**
Many small changes → many messages. Use `BatchingRemoteConnection` or ensure changes happen within the same microtask.

**6. Missing polyfill in workers**
Web workers have no DOM. Import `@remote-dom/polyfill` before any DOM operations.

## Serialization Constraints

**Serialized:** Element tag names, IDs, declared attributes, declared properties, event listener registrations, child relationships.

**NOT serialized:** Functions (use event pattern), DOM node references, complex object graphs, circular references, undeclared properties.

## Performance Tips

- Use `BatchingRemoteConnection` to coalesce mutations within a microtask
- Minimize object property size (serialized fully on each change)
- Prefer attributes for simple string/boolean/number values
- Use event delegation patterns to reduce listener registrations
- Consider `@remote-dom/signals` for fine-grained reactivity
