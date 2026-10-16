
import React from 'react';
import { View, TextInput, Text, StyleSheet } from 'react-native';
import { COLORS, SIZES } from '../constants/theme';
import { Mail, Lock, User, AtSign } from 'lucide-react-native';

const Input = ({ icon, label, placeholder, value, onChangeText, secureTextEntry, error, ...props }) => {
    return (
        <View style={styles.container}>
            {label && <Text style={styles.label}>{label}</Text>}
            <View style={[styles.inputContainer, error && styles.errorInput]}>
                {icon && (
                    <View style={styles.iconContainer}>
                        {icon === 'user' && <User color={COLORS.gray} size={20} />}
                        {icon === 'lock' && <Lock color={COLORS.gray} size={20} />}
                        {icon === 'mail' && <Mail color={COLORS.gray} size={20} />}
                        {icon === 'at-sign' && <AtSign color={COLORS.gray} size={20} />}
                    </View>
                )}
                <TextInput
                    style={styles.input}
                    placeholder={placeholder}
                    placeholderTextColor={COLORS.gray}
                    value={value}
                    onChangeText={onChangeText}
                    secureTextEntry={secureTextEntry}
                    {...props}
                />
            </View>
            {error && <Text style={styles.errorText}>{error}</Text>}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        marginBottom: SIZES.medium,
    },
    label: {
        fontSize: 14,
        color: COLORS.text,
        marginBottom: 4,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        borderWidth: 1,
        borderColor: COLORS.gray,
        borderRadius: SIZES.radius,
        paddingHorizontal: SIZES.medium,
        paddingVertical: SIZES.small,
        backgroundColor: COLORS.white,
    },
    errorInput: {
        borderColor: COLORS.error,
    },
    iconContainer: {
        marginRight: 8,
    },
    input: {
        flex: 1,
        color: COLORS.text,
        fontSize: 16,
    },
    errorText: {
        color: COLORS.error,
        fontSize: 12,
        marginTop: 4,
    },
});

export default Input;
