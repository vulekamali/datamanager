---
category: Universal Components
assets: examples
state:
  text: ✔ stable
  color: white
  background: green
API:
  text: HTML
  color: black
  background: '#CCCCCC'
support:
  text: IE 9
  color: white
  background: grey
---

## Overview

- Component is used to provide user with functionality to share the current page via Facebook, Twitter or just copy as a link.
- For Facebook and Twitter a new window is opened that has the FB / Twitter specific URL with the required query strings.
- To copy the link a modal is opened (via a Redux action creator) with the URL for a user to copy.

## Examples

### Basic (500px)
[View Source](basic.html)
<iframe width="100%" height="350" src="basic.html" frameborder="0" allowfullscreen></iframe>

```
// Redux method

import { createModal } from './../redux.js';

createModal('Example title', 'This is text');
```

### Basic (500px)
[View Source](basic.html)
<iframe width="100%" height="350" src="basic.html" frameborder="0" allowfullscreen></iframe>

```
// Redux method with React markup

import { createModal, removeModal } from './../redux.js';

const markup = (
  <div>
    <h3>This is a heading</h3>
    <p>This is a paragraph</p>
    <button onClick={removeModal}>This is a close button</button>
  </div>
)

createModal('Example title', markup);
```
