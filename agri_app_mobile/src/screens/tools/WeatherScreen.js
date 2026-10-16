
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { COLORS, SIZES } from '../../constants/theme';
import { CloudRain, Sun, Wind } from 'lucide-react-native';
import axios from 'axios';

const WeatherScreen = () => {
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(true);

    // Mock lat/lon for Hyderabad, India
    const lat = 17.3850;
    const lon = 78.4867;
    const API_KEY = 'YOUR_OPENWEATHERMAP_API_KEY'; // Ideally in .env

    useEffect(() => {
        // For demo purposes, I'll mock the response to avoid API key issues in this starter code
        // In production, uncomment the axios call
        setTimeout(() => {
            setWeather({
                main: { temp: 29.5, humidity: 60 },
                weather: [{ description: 'Scattered Clouds', icon: '03d' }],
                wind: { speed: 5.2 }
            });
            setLoading(false);
        }, 1000);

        /*
        axios.get(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric`)
          .then(res => {
            setWeather(res.data);
            setLoading(false);
          })
          .catch(err => {
            console.error(err);
            setLoading(false);
          });
        */
    }, []);

    if (loading) {
        return (
            <View style={styles.centered}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.location}>Hyderabad, India</Text>
                <Text style={styles.date}>{new Date().toDateString()}</Text>
            </View>

            <View style={styles.weatherCard}>
                <Sun color={COLORS.white} size={80} />
                <Text style={styles.temp}>{Math.round(weather?.main?.temp)}°C</Text>
                <Text style={styles.condition}>{weather?.weather[0]?.description}</Text>
            </View>

            <View style={styles.detailsGrid}>
                <View style={styles.detailItem}>
                    <CloudRain color={COLORS.primary} size={24} />
                    <Text style={styles.detailLabel}>Humidity</Text>
                    <Text style={styles.detailValue}>{weather?.main?.humidity}%</Text>
                </View>
                <View style={styles.detailItem}>
                    <Wind color={COLORS.primary} size={24} />
                    <Text style={styles.detailLabel}>Wind Speed</Text>
                    <Text style={styles.detailValue}>{weather?.wind?.speed} m/s</Text>
                </View>
            </View>

            {/* 5-Day Forecast placeholder */}
            <Text style={styles.sectionTitle}>5-Day Forecast</Text>
            {[1, 2, 3, 4, 5].map((day) => (
                <View key={day} style={styles.forecastRow}>
                    <Text style={styles.forecastDay}>Day {day}</Text>
                    <Sun color={COLORS.secondary} size={20} />
                    <Text style={styles.forecastTemp}>30° / 22°</Text>
                </View>
            ))}

        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
        padding: SIZES.medium,
    },
    centered: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    header: {
        alignItems: 'center',
        marginBottom: SIZES.large,
    },
    location: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    date: {
        fontSize: 16,
        color: COLORS.gray,
    },
    weatherCard: {
        backgroundColor: COLORS.primary,
        borderRadius: SIZES.xlarge,
        padding: SIZES.xxlarge,
        alignItems: 'center',
        marginBottom: SIZES.large,
        ...SHADOWS.medium,
    },
    temp: {
        fontSize: 64,
        fontWeight: 'bold',
        color: COLORS.white,
        marginTop: SIZES.medium,
    },
    condition: {
        fontSize: 20,
        color: COLORS.white,
        textTransform: 'capitalize',
        marginTop: SIZES.small,
    },
    detailsGrid: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        marginBottom: SIZES.xlarge,
    },
    detailItem: {
        backgroundColor: COLORS.white,
        padding: SIZES.medium,
        borderRadius: SIZES.radius,
        alignItems: 'center',
        width: '45%',
        ...SHADOWS.small,
    },
    detailLabel: {
        fontSize: 14,
        color: COLORS.gray,
        marginTop: SIZES.small,
    },
    detailValue: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginTop: 4,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10
    },
    forecastRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: 15,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.tertiary,
        alignItems: 'center'
    },
    forecastDay: {
        fontSize: 16,
        color: COLORS.text,
        width: 100
    },
    forecastTemp: {
        fontSize: 16,
        fontWeight: '600'
    }
});

export default WeatherScreen;
