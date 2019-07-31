import { jsConnect } from './../../../utilities/js/helpers/connector';


const callback = ({ image, thumb }) => {
  thumb.style.backgroundImage = `url('${image}')`;
};


jsConnect(callback, 'ThumbPreview', { image: 'string', thumb: null });

