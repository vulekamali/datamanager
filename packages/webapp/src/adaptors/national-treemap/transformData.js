
const transformData = ({ total, items }) => {
  const transformedItems = items.map((props) => {
    const { slug: id, detail: url, percentage_of_total: percentage, ...otherProps } = props;
    return { id, url, percentage, ...otherProps };
  });

  return {
    total,
    items: transformedItems,
  }
}


export default transformData;
