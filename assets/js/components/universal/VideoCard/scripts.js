import { zipObject } from 'lodash';
import { h } from 'preact';
import PropTypes, { checkPropTypes } from 'prop-types';
import { jsConnect } from './../../../utilities/js/helpers/connector';
import { createModal } from './../../header-and-footer/Modals/redux.js';
import VideoEmbed from './../VideoEmbed/index.jsx';


const params = {
  thumbnail: PropTypes.object,
  title: PropTypes.string,
  buttons: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      language: PropTypes.string,
      node: PropTypes.object,
    }),
  ),
};


const query = {
  thumbnail: null,
  title: 'innerText',
  text: null,
  buttons: [
    {
      id: 'string',
      language: 'innerText',
      node: null,
    },
  ],
};


const updateModalState = (title, selected, languages) => {
  return createModal(
    title,
    h(VideoEmbed, { title, languages, initialSelected: selected }),
  );
};

/**
 *  Takes all props passed from HTML React Connector query. Starts by setting background image of
 *  'thumbnail' div to Youtube thumbnail of via JavaScript DOM interface. Due to restrictions on
 *  cross-content permissions inline CSS is not allowed, thus JS needs to be used. The also binds a
 *  Redux action that will load the required video display/switch Preact component inside the modal
 *  component. The latter is bound to the thumbnail on click (with 'English' as default), and then
 *  subsequently for each language button in the VideoCard.
 *
 *  @param {Object} props - An object that holds all the values gathered from HTML.
 *  @param {HTMLElement} props.thumbnail - The Youtube ID of the English version of the video.
 *  @param {string} props.title - The title of the video.
 *  @param {Object[]} props.buttons - An array of containing the id, language name and DOM node of
 *  each language's button.
 *  @returns {null} - Consists exclusively of side-effects.
 */
const callback = (props) => {
  checkPropTypes(params, props, 'argument', 'VideoCard');

  const { thumbnail, title, buttons, text } = props;
  const url = `url('https://img.youtube.com/vi/${buttons[0].id}/mqdefault.jpg')`;
  thumbnail.style.backgroundImage = url;

  const languages = zipObject(buttons.map(val => val.language), buttons.map(val => val.id));

  thumbnail.addEventListener(
    'click',
    () => updateModalState(title, buttons[0].language, languages),
  );

  text.addEventListener(
    'click',
    () => updateModalState(title, buttons[0].language, languages),
  );

  buttons.forEach(({ language, node }) => {
    node.addEventListener(
      'click',
      () => updateModalState(title, language, languages),
    );
  });
};


jsConnect(callback, 'VideoCard', query);
