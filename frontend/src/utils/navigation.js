export const getDashboardPath = (role) => {
  const normalizedRole = role?.toLowerCase();
  switch (normalizedRole) {
    case 'nurse':
      return '/nurse';
    case 'doctor':
      return '/doctor';
    default:
      // Default to login page if role is unknown, null, or undefined
      return '/login';
  }
};
