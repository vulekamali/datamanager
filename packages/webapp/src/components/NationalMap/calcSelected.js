import getById from './getById';


const calcSelected = projects => (id) => { 
  if (!id) {
    return null;
  }

  const project = getById(id, projects);
  return project.points[0];
}


export default calcSelected;
