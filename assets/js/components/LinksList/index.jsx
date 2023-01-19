import PropTypes from 'prop-types';

import Icon from '../Icon/index.jsx';


const buildItem = ({ title, type, link, prefix }) => {
  return (
    <li>
      <a href={link} className="LinksList-link">
        <span className="LinksList-icon"><Icon {...{ type }} size="s" /></span>
        {prefix && <span>{prefix}&nbsp;</span>}
        <span className="LinksList-title">{title}</span>
      </a>
    </li>
  );
};


const LinksList = (props) => {
  const { listArray } = props;

  return (
    <ul className="LinksList">
      {listArray.map(({ title, type, link }) => buildItem({ title, type, link }))}
    </ul>
  );
};


LinksList.propTypes = {
  listArray: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      link: PropTypes.string.isRequired,
      type: PropTypes.string.isRequired,
      prefix: PropTypes.string,
    }),
  ).isRequired,
};


export default LinksList;
