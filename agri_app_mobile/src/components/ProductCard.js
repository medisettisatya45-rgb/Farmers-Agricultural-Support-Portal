
import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../constants/theme';

const ProductCard = ({ product, onPress }) => {
    const imageUrl = product.images && product.images.length > 0
        ? product.images[0]
        : 'https://via.placeholder.com/150';

    return (
        <TouchableOpacity style={styles.card} onPress={onPress}>
            <Image
                source={{ uri: imageUrl }}
                style={styles.image}
                resizeMode="cover"
            />
            <View style={styles.content}>
                <Text style={styles.name} numberOfLines={1}>{product.name}</Text>
                <Text style={styles.price}>₹{product.price}/kg</Text>
                <Text style={styles.category}>{product.category_name}</Text>
                <TouchableOpacity style={styles.addButton}>
                    <Text style={styles.addButtonText}>Add</Text>
                </TouchableOpacity>
            </View>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: COLORS.white,
        borderRadius: SIZES.radius,
        marginBottom: SIZES.medium,
        width: '48%',
        ...SHADOWS.small,
        overflow: 'hidden',
    },
    image: {
        width: '100%',
        height: 120,
        backgroundColor: COLORS.background,
    },
    content: {
        padding: SIZES.small,
    },
    name: {
        fontSize: 14,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 4,
    },
    price: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginBottom: 4,
    },
    category: {
        fontSize: 12,
        color: COLORS.gray,
        marginBottom: 8,
    },
    addButton: {
        backgroundColor: COLORS.secondary,
        paddingVertical: 4,
        borderRadius: 4,
        alignItems: 'center',
    },
    addButtonText: {
        color: COLORS.white,
        fontWeight: '600',
        fontSize: 12,
    },
});

export default ProductCard;
