const isPointId = pointId => id => id === pointId;

const findProject = projects => (pointId) => { 
  if (!pointId) {
    return {};
  }
  
  for (let i = 0; i < projects.length; i++) {
    const project = projects[i];

    if (!!project.points.find(isPointId(pointId))) {
      return project;
    }
  }

  return {};
}


export default findProject;
