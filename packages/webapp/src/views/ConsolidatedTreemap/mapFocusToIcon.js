const mapFocusToIcon = focusName => {
  switch (focusName) {
    case 'agriculture-rural-development-and-land-reform':
      return 'plant';
    case 'basic-education':
      return 'education';
    case 'contingency-reserve':
      return 'money';
    case 'debt-service-costs':
      return 'dollar';
    case 'defence-public-order-and-safety':
      return 'shield';
    case 'economic-affairs':
      return 'growth';
    case 'general-public-services':
      return 'person';
    case 'health':
      return 'health';
    case 'human-settlements-and-municipal-infrastructure':
      return 'tap';
    case 'post-school-education-and-training':
      return 'training';
    case 'social-protection':
      return 'family';
    case 'community-development':
      return 'community';
    case 'economic-development':
      return 'growth';
    case 'learning-and-culture':
      return 'education';
    case 'peace-and-security':
      return 'police';
    case 'social-development':
      return 'family';
    default:
      return null;
  }
};

export default mapFocusToIcon;
