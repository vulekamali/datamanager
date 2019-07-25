import { dispatch } from './../../../reduxStore.js';


const CREATE_MODAL = 'CREATE_MODAL';
const REMOVE_MODAL = 'REMOVE_MODAL';


export function createModal(title, markup) {
  return dispatch({
    type: CREATE_MODAL,
    payload: {
      title,
      markup,
    },
  });
}

export function removeModal() {
  return dispatch({ type: REMOVE_MODAL });
}


export default function reducer(state = {}, action) {
  switch (action.type) {
    case 'CREATE_MODAL':
      return {
        ...state,
        modal: {
          title: action.payload.title,
          markup: action.payload.markup,
        },
      };

    case 'REMOVE_MODAL':
      return {
        ...state,
        modal: null,
      };

    default: return state;
  }
}
