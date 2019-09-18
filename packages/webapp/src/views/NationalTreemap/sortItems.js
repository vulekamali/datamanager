const sortSingleItem = ({ amount: a }, { amount: b }) => b - a;

const sortItems = items => {
  const sortedChildren = items.map(item => ({
    ...item,
    children: item.children ? item.children.sort(sortSingleItem) : null,
  }));
  return sortedChildren.sort(sortSingleItem);
};

export default sortItems;
