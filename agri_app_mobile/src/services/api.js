
import axios from 'axios';
import { Platform } from 'react-native';

// IMPORTANT: Replace with your computer's local IP address if running on a physical device.
// run `ipconfig` (Windows) or `ifconfig` (Mac/Linux) to find it.
// Android Emulator uses 10.0.2.2 for localhost.
// iOS Simulator uses localhost.

// Helper to determine base URL
const getBaseUrl = () => {
    if (Platform.OS === 'android') {
        return 'http://10.0.2.2:5000/api';
    }
    return 'http://localhost:5000/api'; // iOS Simulator
    // return 'http://192.168.1.X:5000/api'; // Use this for physical device
};

const API_URL = getBaseUrl();

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000, // 10 seconds timeout
});

// Add a responsive interceptor to handle errors globally if needed
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Modify this to handle specific errors like 401 Unauthorized
        if (error.response && error.response.status === 401) {
            console.log('Unauthorized access - redirect to login');
            // Logic to clear storage and navigate to login could go here
        }
        return Promise.reject(error);
    }
);

export default api;
