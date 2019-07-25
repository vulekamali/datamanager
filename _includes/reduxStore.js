import { createStore } from 'redux';
import modalReducers from './components/header-and-footer/Modals/redux.js';

/* eslint-disable no-underscore-dangle */
const store = createStore(
  modalReducers,
  {},
  window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__(),
);
/* eslint-enable */

const { dispatch, subscribe, getState } = store;

export { dispatch, subscribe, getState };
export default store;
