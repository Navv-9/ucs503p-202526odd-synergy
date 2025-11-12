export const INDIAN_CITIES = [
  // Punjab
  'Patiala',
  'Chandigarh',
  'Mohali',
  'Ludhiana',
  'Amritsar',
  'Jalandhar',
  'Bathinda',
  'Pathankot',
  
  // Other major cities
  'Delhi',
  'Mumbai',
  'Bangalore',
  'Hyderabad',
  'Chennai',
  'Kolkata',
  'Pune',
  'Ahmedabad',
  'Jaipur',
  'Surat',
  'Lucknow',
  'Kanpur',
  'Nagpur',
  'Indore',
  'Thane',
  'Bhopal',
  'Visakhapatnam',
  'Vadodara',
  'Ghaziabad',
  'Noida',
  'Faridabad',
  'Gurgaon',
  'Mysore',
  'Coimbatore',
  'Kochi',
];

export const detectCityFromIP = async () => {
  try {
    const response = await fetch('https://ipapi.co/json/');
    const data = await response.json();
    return data.city || 'Patiala';
  } catch (error) {
    console.error('Failed to detect city:', error);
    return 'Patiala';
  }
};