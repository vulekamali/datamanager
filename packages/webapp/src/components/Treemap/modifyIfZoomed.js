const modifyIfZoomed = (items, zoom) => {
  if (!zoom) {
    return items;
  }

  const result = items.find(({ name }) => name === zoom).children;
  return result;
}


export default modifyIfZoomed;
