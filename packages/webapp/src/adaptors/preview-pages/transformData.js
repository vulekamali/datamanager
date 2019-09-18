const changeUrls = ({ url, ...otherValues }) => ({
  ...otherValues,
  url: url && `/${url}`,
});

const createProgrammeObject = ({ amount, title }) => ({
  amount,
  title,
});

const transformData = response => {
  const departmentSchema = response.items.map(department => {
    const {
      percentage_of_budget: percentage,
      total,
      programmes,
      description,
      title,
      slug,
      url,
      focus_areas: focusAreas,
    } = department;

    return {
      resources: {
        consolidated: percentage,
        value: total,
      },
      items: programmes.map(createProgrammeObject),
      description,
      title,
      id: slug,
      url,
      focusAreas: focusAreas.map(changeUrls),
    };
  });

  return departmentSchema;
};

export default transformData;
