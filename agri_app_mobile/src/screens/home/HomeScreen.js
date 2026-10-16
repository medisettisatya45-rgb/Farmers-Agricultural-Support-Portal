
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, ImageBackground } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import { Sun, CloudRain, Thermometer, Sprout, DollarSign, ShoppingBag, BarChart2, PlusCircle, AlertCircle, FileText, MessageCircle } from 'lucide-react-native';
import api from '../../services/api';

const FeatureCard = ({ title, icon, onPress, color }) => (
    <TouchableOpacity style={[styles.featureCard, { backgroundColor: color || COLORS.white }]} onPress={onPress}>
        <View style={styles.iconContainer}>
            {icon}
        </View>
        <Text style={styles.featureTitle}>{title}</Text>
    </TouchableOpacity>
);

const HomeScreen = ({ navigation }) => {
    const [refreshing, setRefreshing] = useState(false);
    const [weatherData, setWeatherData] = useState(null);

    const fetchWeather = async () => {
        // Mock weather data fetch or real API if backend supports it
        // For now, static mock to ensure UI works
        setWeatherData({
            temp: '28°C',
            condition: 'Sunny',
            humidity: '65%'
        });
    };

    const onRefresh = React.useCallback(() => {
        setRefreshing(true);
        fetchWeather().then(() => setRefreshing(false));
    }, []);

    useEffect(() => {
        fetchWeather();
    }, []);

    return (
        <ScrollView
            style={styles.container}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        >
            {/* Header Section */}
            <View style={styles.header}>
                <View>
                    <Text style={styles.greeting}>Namaste, Farmer!</Text>
                    <Text style={styles.subGreeting}>Welcome to your dashboard</Text>
                </View>
                <TouchableOpacity onPress={() => navigation.navigate('Profile')}>
                    {/* Profile Icon Placeholder */}
                    <View style={styles.profileIcon} />
                </TouchableOpacity>
            </View>

            {/* Weather Widget */}
            <View style={styles.weatherCard}>
                <View style={styles.weatherInfo}>
                    <Text style={styles.weatherTemp}>{weatherData?.temp || '--'}</Text>
                    <Text style={styles.weatherCondition}>{weatherData?.condition || 'Loading...'}</Text>
                    <Text style={styles.weatherLocation}>Hyderabad, India</Text>
                </View>
                <CloudRain color={COLORS.white} size={48} />
            </View>

            {/* Quick Tools Grid */}
            <Text style={styles.sectionTitle}>Farming Tools</Text>
            <View style={styles.grid}>
                <FeatureCard
                    title="Crop Doctor"
                    icon={<Sprout color={COLORS.primary} size={32} />}
                    onPress={() => navigation.navigate('CropRecommendation')}
                />
                <FeatureCard
                    title="Fertilizers"
                    icon={<BarChart2 color={COLORS.secondary} size={32} />}
                    onPress={() => navigation.navigate('FertilizerGuide')}
                />
                <FeatureCard
                    title="Cost Calc"
                    icon={<DollarSign color={COLORS.text} size={32} />}
                    onPress={() => navigation.navigate('CostEstimator')}
                />
                <FeatureCard
                    title="Weather"
                    icon={<Sun color="#FBC02D" size={32} />}
                    onPress={() => navigation.navigate('Weather')}
                />
                <FeatureCard
                    title="Disease Detection"
                    icon={<AlertCircle color={COLORS.error} size={32} />}
                    onPress={() => navigation.navigate('DiseaseDetection')}
                />
                <FeatureCard
                    title="Govt Schemes"
                    icon={<FileText color={COLORS.primary} size={32} />}
                    onPress={() => navigation.navigate('GovernmentSchemes')}
                />
                <FeatureCard
                    title="Expert Chat"
                    icon={<MessageCircle color={COLORS.secondary} size={32} />}
                    onPress={() => navigation.navigate('ExpertChat')}
                />
            </View>

            {/* Market Actions */}
            <Text style={styles.sectionTitle}>Marketplace</Text>
            <View style={styles.marketActions}>
                <TouchableOpacity
                    style={[styles.actionButton, { backgroundColor: COLORS.tertiary }]}
                    onPress={() => navigation.navigate('ProductListing')}
                >
                    <ShoppingBag color={COLORS.primary} size={24} />
                    <Text style={styles.actionText}>Buy Seeds/Products</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.actionButton, { backgroundColor: COLORS.primary }]}
                    onPress={() => navigation.navigate('SellProduct')}
                >
                    <PlusCircle color={COLORS.white} size={24} />
                    <Text style={[styles.actionText, { color: COLORS.white }]}>Sell Your Produce</Text>
                </TouchableOpacity>
            </View>

            {/* Recent Activity or News could go here */}
            <View style={styles.spacer} />
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        padding: SIZES.medium,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: SIZES.medium, // Safe area top handled by SafeAreaView in Navigator usually, but good to add some
    },
    greeting: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    subGreeting: {
        fontSize: 14,
        color: COLORS.gray,
    },
    profileIcon: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: COLORS.secondary,
    },
    weatherCard: {
        margin: SIZES.medium,
        padding: SIZES.large,
        backgroundColor: COLORS.primary,
        borderRadius: SIZES.radius,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        ...SHADOWS.medium,
    },
    weatherInfo: {
        flex: 1,
    },
    weatherTemp: {
        fontSize: 32,
        fontWeight: 'bold',
        color: COLORS.white,
    },
    weatherCondition: {
        fontSize: 18,
        color: COLORS.white,
        opacity: 0.9,
    },
    weatherLocation: {
        fontSize: 14,
        color: COLORS.white,
        opacity: 0.8,
        marginTop: 4,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginLeft: SIZES.medium,
        marginTop: SIZES.medium,
        marginBottom: SIZES.small,
    },
    grid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        paddingHorizontal: SIZES.small,
    },
    featureCard: {
        width: '45%',
        margin: '2.5%',
        padding: SIZES.medium,
        borderRadius: SIZES.radius,
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: COLORS.white,
        aspectRatio: 1,
        ...SHADOWS.small,
    },
    iconContainer: {
        marginBottom: SIZES.small,
        padding: SIZES.small,
        backgroundColor: COLORS.background,
        borderRadius: 50,
    },
    featureTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: COLORS.text,
        textAlign: 'center',
    },
    marketActions: {
        paddingHorizontal: SIZES.medium,
        gap: SIZES.medium,
    },
    actionButton: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: SIZES.medium,
        borderRadius: SIZES.radius,
        marginBottom: SIZES.small,
        ...SHADOWS.small,
    },
    actionText: {
        marginLeft: SIZES.medium,
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    spacer: {
        height: 100,
    }
});

export default HomeScreen;
