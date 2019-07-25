const provincialName = {
  'eastern-cape': 'Eastern Cape',
  'free-state': 'Free State',
  'gauteng': 'Gauteng',
  'kwazulu-natal': 'KwaZulu-Natal',
  'limpopo': 'Limpopo',
  'mpumalanga': 'Mpumalanga',
  'north-west': 'North West',
  'northern-cape': 'Northern Cape',
  'western-cape': 'Western Cape',
}

const calcPrettyName = governmentSlug => {
  if (governmentSlug === 'south-africa') {
    return 'National Budget';
  }
  return provincialName[governmentSlug];
};

export default calcPrettyName;
