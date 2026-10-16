
import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../constants/theme';

const Button = ({ title, onPress, type = 'primary', disabled = false, style }) => {
    const getBackgroundColor = () => {
        if (disabled) return COLORS.gray;
        switch (type) {
            case 'primary': return COLORS.primary;
            case 'secondary': return COLORS.secondary;
            case 'outline': return 'transparent';
            case 'text': return 'transparent';
            default: return COLORS.primary;
        }
    };

    const getTextColor = () => {
        if (disabled) return COLORS.white;
        switch (type) {
            case 'primary': return COLORS.white;
            case 'secondary': return COLORS.white;
            case 'outline': return COLORS.primary;
            case 'text': return COLORS.primary;
            default: return COLORS.white;
        }
    };

    const borderStyles = type === 'outline' ? { borderWidth: 1, borderColor: COLORS.primary } : {};

    return (
        <TouchableOpacity
            style={[
                styles.button,
                { backgroundColor: getBackgroundColor() },
                borderStyles,
                style
            ]}
            onPress={onPress}
            disabled={disabled}
        >
            <Text style={[styles.text, { color: getTextColor() }]}>{title}</Text>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    button: {
        paddingVertical: SIZES.medium,
        paddingHorizontal: SIZES.large,
        borderRadius: SIZES.radius,
        alignItems: 'center',
        justifyContent: 'center',
        ...SHADOWS.small,
    },
    text: {
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default Button;
