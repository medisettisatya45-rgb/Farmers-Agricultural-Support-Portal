
import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert, KeyboardAvoidingView, Platform } from 'react-native';
import { COLORS, SIZES } from '../../constants/theme';
import Button from '../../components/Button';
import Input from '../../components/Input';
import api from '../../services/api';

const SignupScreen = ({ navigation }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSignup = async () => {
        if (!username || !password || !email || !confirmPassword) {
            Alert.alert('Error', 'Please fill all required fields');
            return;
        }

        if (password !== confirmPassword) {
            Alert.alert('Error', 'Passwords do not match');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/register', {
                username,
                password,
                confirm_password: confirmPassword,
                email,
                phone
            });

            if (response.data.success) {
                Alert.alert('Success', 'Account Created Successfully');
                navigation.navigate('Login');
            } else {
                Alert.alert('Registration Failed', response.data.message || 'Could not register');
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
                    <Text style={styles.title}>Create Account</Text>
                    <Text style={styles.subtitle}>Join AgriApp Today</Text>
                </View>

                <View style={styles.form}>
                    <View style={{ marginBottom: 15 }}>
                        <Text style={styles.label}>Username *</Text>
                        <Input
                            placeholder="Choose a username"
                            value={username}
                            onChangeText={setUsername}
                            autoCapitalize="none"
                        />
                    </View>

                    <View style={{ marginBottom: 15 }}>
                        <Text style={styles.label}>Email *</Text>
                        <Input
                            placeholder="Enter your email"
                            value={email}
                            onChangeText={setEmail}
                            keyboardType="email-address"
                            autoCapitalize="none"
                        />
                    </View>

                    <View style={{ marginBottom: 15 }}>
                        <Text style={styles.label}>Phone (Optional)</Text>
                        <Input
                            placeholder="Enter your phone number"
                            value={phone}
                            onChangeText={setPhone}
                            keyboardType="phone-pad"
                        />
                    </View>

                    <View style={{ marginBottom: 15 }}>
                        <Text style={styles.label}>Password *</Text>
                        <Input
                            placeholder="Create a password"
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry
                        />
                    </View>

                    <View style={{ marginBottom: 25 }}>
                        <Text style={styles.label}>Confirm Password *</Text>
                        <Input
                            placeholder="Confirm your password"
                            value={confirmPassword}
                            onChangeText={setConfirmPassword}
                            secureTextEntry
                        />
                    </View>

                    <Button
                        title={loading ? "Creating Account..." : "Sign Up"}
                        onPress={handleSignup}
                        disabled={loading}
                    />

                    <View style={styles.footer}>
                        <Text style={styles.footerText}>Already have an account? </Text>
                        <Text
                            style={styles.link}
                            onPress={() => navigation.navigate('Login')}
                        >
                            Login
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
        marginBottom: SIZES.large,
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

export default SignupScreen;
