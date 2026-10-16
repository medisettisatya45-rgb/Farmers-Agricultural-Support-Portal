
import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, Image } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import Button from '../../components/Button';
import { User, LogOut, ShoppingBag, Settings, MapPin, CreditCard } from 'lucide-react-native';
import api from '../../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ProfileMenuItem = ({ icon, title, onPress }) => (
    <TouchableOpacity style={styles.menuItem} onPress={onPress}>
        <View style={styles.menuIconContainer}>
            {icon}
        </View>
        <Text style={styles.menuTitle}>{title}</Text>
        <Text style={styles.menuArrow}>›</Text>
    </TouchableOpacity>
);

const ProfileScreen = ({ navigation }) => {
    // Mock user data or fetch from storage/context
    const user = {
        name: 'Ramesh Kumar',
        email: 'ramesh.kumar@example.com',
        image: 'https://via.placeholder.com/150'
    };

    const handleLogout = async () => {
        Alert.alert(
            "Logout",
            "Are you sure you want to logout?",
            [
                { text: "Cancel", style: "cancel" },
                {
                    text: "Logout",
                    onPress: async () => {
                        try {
                            // await AsyncStorage.clear();
                            // await api.post('/logout');
                            navigation.replace('Login');
                        } catch (e) {
                            console.error(e);
                        }
                    }
                }
            ]
        );
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <View style={styles.profileImageContainer}>
                    <Image source={{ uri: user.image }} style={styles.profileImage} />
                </View>
                <Text style={styles.name}>{user.name}</Text>
                <Text style={styles.email}>{user.email}</Text>
                <Button
                    title="Edit Profile"
                    type="outline"
                    style={styles.editButton}
                    onPress={() => { }}
                />
            </View>

            <View style={styles.menuContainer}>
                <Text style={styles.sectionTitle}>Account</Text>
                <ProfileMenuItem
                    icon={<ShoppingBag color={COLORS.primary} size={20} />}
                    title="My Orders"
                    onPress={() => { }}
                />
                <ProfileMenuItem
                    icon={<MapPin color={COLORS.primary} size={20} />}
                    title="Delivery Address"
                    onPress={() => { }}
                />
                <ProfileMenuItem
                    icon={<CreditCard color={COLORS.primary} size={20} />}
                    title="Payment Methods"
                    onPress={() => { }}
                />

                <Text style={styles.sectionTitle}>Settings</Text>
                <ProfileMenuItem
                    icon={<Settings color={COLORS.primary} size={20} />}
                    title="App Settings"
                    onPress={() => { }}
                />
                <ProfileMenuItem
                    icon={<LogOut color={COLORS.error} size={20} />}
                    title="Logout"
                    onPress={handleLogout}
                />
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        alignItems: 'center',
        padding: SIZES.xlarge,
        backgroundColor: COLORS.white,
        borderBottomLeftRadius: SIZES.xlarge,
        borderBottomRightRadius: SIZES.xlarge,
        ...SHADOWS.small,
    },
    profileImageContainer: {
        width: 100,
        height: 100,
        borderRadius: 50,
        overflow: 'hidden',
        marginBottom: SIZES.medium,
        borderWidth: 3,
        borderColor: COLORS.secondary,
    },
    profileImage: {
        width: '100%',
        height: '100%',
    },
    name: {
        fontSize: 22,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 4,
    },
    email: {
        fontSize: 16,
        color: COLORS.gray,
        marginBottom: SIZES.medium,
    },
    editButton: {
        paddingVertical: SIZES.small,
        paddingHorizontal: SIZES.large,
        width: 150,
    },
    menuContainer: {
        padding: SIZES.medium,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginTop: SIZES.medium,
        marginBottom: SIZES.small,
        marginLeft: SIZES.small,
    },
    menuItem: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.white,
        padding: SIZES.medium,
        borderRadius: SIZES.radius,
        marginBottom: SIZES.small,
        ...SHADOWS.small,
    },
    menuIconContainer: {
        marginRight: SIZES.medium,
        padding: 8,
        backgroundColor: COLORS.background,
        borderRadius: 8,
    },
    menuTitle: {
        flex: 1,
        fontSize: 16,
        color: COLORS.text,
        fontWeight: '500',
    },
    menuArrow: {
        fontSize: 20,
        color: COLORS.gray,
    },
});

export default ProfileScreen;
