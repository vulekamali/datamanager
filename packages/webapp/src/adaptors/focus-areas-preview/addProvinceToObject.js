const addProvinceToObject = provincialData => {
  if (provincialData.length === 0) {
    return {};
  }

  return [
    'Eastern Cape',
    'Free State',
    'Gauteng',
    'Limpopo',
    'Mpumalanga',
    'Northern Cape',
    'Western Cape',
    'North West',
    'KwaZulu-Natal',
  ].reduce((result, provinceName) => {
    const children = provincialData
      .filter(item => item.province === provinceName)
      .map(({ slug, percentage_of_total, url, ...data }) => ({
        ...data,
        id: slug,
        percentage: percentage_of_total,
        url: url && `/${url}`,
      }));

    const amount = children.reduce((result, { amount }) => result + amount, 0);

    return {
      ...result,
      [provinceName]: {
        name: provinceName,
        amount,
        children,
      },
    };
  }, {});
};

export default addProvinceToObject;
