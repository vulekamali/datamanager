const getById = (id, array = []) => {
  return array.find(({ id: itemId }) => itemId === id);
}


export default getById;
