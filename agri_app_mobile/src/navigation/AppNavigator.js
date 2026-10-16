
import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { NavigationContainer } from '@react-navigation/native';
import { COLORS } from '../constants/theme';
import { Home, ShoppingBag, ShoppingCart, User } from 'lucide-react-native';

// Screens
import SplashScreen from '../screens/SplashScreen';
import LoginScreen from '../screens/auth/LoginScreen';
import SignupScreen from '../screens/auth/SignupScreen';
import HomeScreen from '../screens/home/HomeScreen';
import ProductListingScreen from '../screens/market/ProductListingScreen';
import ProductDetailsScreen from '../screens/market/ProductDetailsScreen';
import CartScreen from '../screens/cart/CartScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import SellProductScreen from '../screens/profile/SellProductScreen';
import CropRecommendationScreen from '../screens/tools/CropRecommendationScreen';
import FertilizerGuideScreen from '../screens/tools/FertilizerGuideScreen';
import CostEstimatorScreen from '../screens/tools/CostEstimatorScreen';
import WeatherScreen from '../screens/tools/WeatherScreen';
import DiseaseDetectionScreen from '../screens/tools/DiseaseDetectionScreen';
import GovernmentSchemesScreen from '../screens/tools/GovernmentSchemesScreen';
import ExpertChatScreen from '../screens/tools/ExpertChatScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const MainTabs = () => {
    return (
        <Tab.Navigator
            screenOptions={{
                headerShown: false,
                tabBarActiveTintColor: COLORS.primary,
                tabBarInactiveTintColor: COLORS.gray,
                tabBarStyle: {
                    borderTopWidth: 0,
                    elevation: 5,
                    height: 60,
                    paddingBottom: 10,
                },
                tabBarLabelStyle: {
                    fontSize: 12,
                    fontWeight: '600'
                }
            }}
        >
            <Tab.Screen
                name="Home"
                component={HomeScreen}
                options={{
                    tabBarIcon: ({ color }) => <Home color={color} size={24} />
                }}
            />
            <Tab.Screen
                name="Market"
                component={ProductListingScreen}
                options={{
                    tabBarIcon: ({ color }) => <ShoppingBag color={color} size={24} />
                }}
            />
            <Tab.Screen
                name="Cart"
                component={CartScreen}
                options={{
                    tabBarIcon: ({ color }) => <ShoppingCart color={color} size={24} />
                }}
            />
            <Tab.Screen
                name="Profile"
                component={ProfileScreen}
                options={{
                    tabBarIcon: ({ color }) => <User color={color} size={24} />
                }}
            />
        </Tab.Navigator>
    );
};

const AppNavigator = () => {
    return (
        <NavigationContainer>
            <Stack.Navigator screenOptions={{ headerShown: false }} initialRouteName="Splash">

                {/* Splash Screen */}
                <Stack.Screen name="Splash" component={SplashScreen} />

                {/* Auth Flow */}
                <Stack.Screen name="Login" component={LoginScreen} />
                <Stack.Screen name="Signup" component={SignupScreen} options={{ headerShown: true, title: '' }} />

                {/* Main App */}
                <Stack.Screen name="Main" component={MainTabs} />

                {/* Feature Screens */}
                <Stack.Screen
                    name="ProductDetails"
                    component={ProductDetailsScreen}
                    options={{ headerShown: true, title: 'Product Details' }}
                />
                <Stack.Screen
                    name="SellProduct"
                    component={SellProductScreen}
                    options={{ headerShown: true, title: 'Sell Product' }}
                />
                <Stack.Screen
                    name="CropRecommendation"
                    component={CropRecommendationScreen}
                    options={{ headerShown: true, title: 'Crop Doctor' }}
                />
                <Stack.Screen
                    name="FertilizerGuide"
                    component={FertilizerGuideScreen}
                    options={{ headerShown: true, title: 'Fertilizer Guide' }}
                />
                <Stack.Screen
                    name="CostEstimator"
                    component={CostEstimatorScreen}
                    options={{ headerShown: true, title: 'Cost Estimator' }}
                />
                <Stack.Screen
                    name="Weather"
                    component={WeatherScreen}
                    options={{ headerShown: true, title: 'Weather Forecast' }}
                />
                <Stack.Screen
                    name="DiseaseDetection"
                    component={DiseaseDetectionScreen}
                    options={{ headerShown: true, title: 'Disease Detection' }}
                />
                <Stack.Screen
                    name="GovernmentSchemes"
                    component={GovernmentSchemesScreen}
                    options={{ headerShown: true, title: 'Government Schemes' }}
                />
                <Stack.Screen
                    name="ExpertChat"
                    component={ExpertChatScreen}
                    options={{ headerShown: true, title: 'Expert Chat' }}
                />
            </Stack.Navigator>
        </NavigationContainer>
    );
};

export default AppNavigator;
