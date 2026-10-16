
import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert, KeyboardAvoidingView, Platform } from 'react-native';
import { COLORS, SIZES } from '../../constants/theme';
import Button from '../../components/Button';
import Input from '../../components/Input'; // Assuming input component exists or use default
import api from '../../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage'; // Need to install this if not present, but I'll assume standard expo flow or add it.

// Note: I might need to install async-storage if it's not strictly in "blank" template by default, 
// but standard React Native flows use it. 
// I will check dependencies later or just use it.
// Actually, let's use a simple mock for now if package is missing, 
// but sticking to standard best practices, use AsyncStorage.
// For now, I will omit the import if I haven't installed it, 
// checking the previous install command... I didn't install async-storage.
// I should install it. 

// Let's write the code assuming it will be available, and I will issue an install command next.

const LoginScreen = ({ navigation }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async () => {
        if (!username || !password) {
            Alert.alert('Error', 'Please enter both username and password');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/login', { username, password });

            if (response.data.success) {
                // Store token/user info (mocking storage for now until package installed)
                // await AsyncStorage.setItem('user', JSON.stringify(response.data.user)); 
                Alert.alert('Success', 'Login Successful');
                navigation.replace('Main');
            } else {
                Alert.alert('Login Failed', response.data.message || 'Invalid credentials');
            }
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            style={styles.container}
        >
            <ScrollView contentContainerStyle={styles.scrollContent}>
                <View style={styles.header}>
                    <Text style={styles.title}>Welcome Back!</Text>
                    <Text style={styles.subtitle}>Login to AgriApp</Text>
                </View>

                <View style={styles.form}>
                    {/* Custom Input would be used here, simplifying for this file content if Input.js is simple */}
                    <View style={{ marginBottom: 15 }}>
                        <Text style={styles.label}>Username</Text>
                        <Input
                            placeholder="Enter your username"
                            value={username}
                            onChangeText={setUsername}
                            autoCapitalize="none"
                        />
                    </View>

                    <View style={{ marginBottom: 25 }}>
                        <Text style={styles.label}>Password</Text>
                        <Input
                            placeholder="Enter your password"
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry
                        />
                    </View>

                    <Button
                        title={loading ? "Logging in..." : "Login"}
                        onPress={handleLogin}
                        disabled={loading}
                    />

                    <View style={styles.footer}>
                        <Text style={styles.footerText}>Don't have an account? </Text>
                        <Text
                            style={styles.link}
                            onPress={() => navigation.navigate('Signup')}
                        >
                            Sign Up
                        </Text>
                    </View>
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    scrollContent: {
        flexGrow: 1,
        padding: SIZES.large,
        justifyContent: 'center',
    },
    header: {
        marginBottom: SIZES.xxlarge,
        alignItems: 'center',
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginBottom: SIZES.small,
    },
    subtitle: {
        fontSize: 16,
        color: COLORS.gray,
    },
    form: {
        width: '100%',
    },
    label: {
        marginBottom: 5,
        fontWeight: '600',
        color: COLORS.dark

    },
    footer: {
        flexDirection: 'row',
        marginTop: SIZES.xlarge,
        justifyContent: 'center',
    },
    footerText: {
        color: COLORS.gray,
        fontSize: 16,
    },
    link: {
        color: COLORS.primary,
        fontWeight: 'bold',
        fontSize: 16,
    },
});

export default LoginScreen;
