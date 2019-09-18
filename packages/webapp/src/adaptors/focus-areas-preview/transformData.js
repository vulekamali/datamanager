import addProvinceToObject from './addProvinceToObject';

const createNationalDepartments = ({ title, amount, url }) => ({
  name: title,
  amount,
  url: url && `/${url}`
});


const transformData = (response) => {
  const focusSchema = response.items.map(department => {
    const {
      national,
      title,
      slug,
      provincial
    } = department;

    const { notices: nationalNotices, footnotes: nationalFootnotes, data: nationalData, total: nationalTotal } = national;

    const { notices: provincialNotices, footnotes: provincialFootnotes, data: provincialData, total: provincialTotal } = provincial;

    return {
      name: title,
      id: slug,
      national: {
        notices: nationalNotices,
        footnotes: nationalFootnotes,
        departments: nationalData.map(createNationalDepartments),
        total: nationalTotal
      },
      provincial: {
        notices: provincialNotices,
        footnotes: provincialFootnotes,
        provinces: addProvinceToObject(provincialData),
        total: provincialTotal
      }
    }
  })

 return focusSchema;

};

export default transformData;
