
import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { COLORS } from '../constants/theme';
import { Sprout } from 'lucide-react-native';

const SplashScreen = ({ navigation }) => {
    const fadeAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        Animated.sequence([
            Animated.timing(fadeAnim, {
                toValue: 1,
                duration: 1000,
                useNativeDriver: true,
            }),
            Animated.delay(1000),
            Animated.timing(fadeAnim, {
                toValue: 0,
                duration: 500,
                useNativeDriver: true,
            }),
        ]).start(() => {
            // Check auth state here if implemented, else go to Login
            // For demo, go to Login
            navigation.replace('Login');
        });
    }, []);

    return (
        <View style={styles.container}>
            <Animated.View style={[styles.content, { opacity: fadeAnim }]}>
                <Sprout color={COLORS.white} size={80} />
                <Text style={styles.title}>AgriApp</Text>
                <Text style={styles.subtitle}>Empowering Farmers</Text>
            </Animated.View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.primary,
        justifyContent: 'center',
        alignItems: 'center',
    },
    content: {
        alignItems: 'center',
    },
    title: {
        fontSize: 40,
        fontWeight: 'bold',
        color: COLORS.white,
        marginTop: 20,
    },
    subtitle: {
        fontSize: 18,
        color: COLORS.tertiary,
        marginTop: 10,
        letterSpacing: 1,
    },
});

export default SplashScreen;
