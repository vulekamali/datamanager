const getCircleStyling = name => ({ hover, selected }) => {
  if (selected && name === 'fill') {
    return 'white';
  }

  if (hover && !selected) {
    if (name === 'transform') {
      return 'translateY(-2px)'
    }

    return 'black';
  }

  if (name === 'transform') {
    return 'translateY(0)'
  }

  if (name === 'fill') {
    return '#5F5F5F'
  }
  return '';
}


export default getCircleStyling;