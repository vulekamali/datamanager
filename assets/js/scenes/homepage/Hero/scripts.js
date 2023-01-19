
import { jsConnect as connect } from '../../../utilities/js/helpers/connector.js';
import VideoEmbed from '../../../components/universal/VideoEmbed/index.jsx';
import { createModal } from '../../../components/header-and-footer/Modals/redux.js';


const callback = (node, path) => {
  node.style.backgroundImage = `url('${path}')`;
};


const videoConfig = {
  title: 'About the Online Budget Data Portal project',
  initialSelected: 'English',
  languages: {
    English: 'zFalZt862hk',
    Afrikaans: 'jsT2YFRDETk',
    isiZulu: 'lMUqzosN6ck',
    isiXhosa: 'nHUDu2SJ9DQ',
    Sesotho: 'lUbcKHxnGkI',
  },
};


const Hero = ({ node, image, button }) => {
  const playVideo = () => createModal(
    videoConfig.title,
    h(VideoEmbed, videoConfig, null),
  );

  button.addEventListener('click', playVideo);

  const virtualImage = new Image();
  virtualImage.src = image;
  virtualImage.onload = () => callback(node, image);
};


const query = {
  node: null,
  image: 'string',
  button: null,
};


export default connect(Hero, 'Hero', query);
