
import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import Button from '../../components/Button';
import { Star, ShoppingCart } from 'lucide-react-native';
import api from '../../services/api';

const ProductDetailsScreen = ({ route, navigation }) => {
    const { product } = route.params;
    const [loading, setLoading] = useState(false);
    const [quantity, setQuantity] = useState(1);

    const handleAddToCart = async () => {
        setLoading(true);
        try {
            await api.post('/cart', {
                product_id: product.product_id,
                quantity
            });

            Alert.alert('Success', 'Product added to cart!');
            navigation.navigate('Cart');
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'Could not add to cart.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <ScrollView style={styles.container}>
            <Image
                source={{ uri: product.image_url || 'https://via.placeholder.com/300' }}
                style={styles.image}
            />

            <View style={styles.detailsContainer}>
                <View style={styles.headerRow}>
                    <Text style={styles.name}>{product.name}</Text>
                    <Text style={styles.price}>₹{product.price}/kg</Text>
                </View>

                <View style={styles.ratingRow}>
                    <Star color={COLORS.secondary} fill={COLORS.secondary} size={16} />
                    <Text style={styles.ratingText}>{product.average_rating || '4.5'} ({product.rating_count || 10} reviews)</Text>
                </View>

                <Text style={styles.sectionTitle}>Description</Text>
                <Text style={styles.description}>
                    {product.description || 'No description available for this product. Fresh from the farm!'}
                </Text>

                <Text style={styles.sectionTitle}>Quantity (kg)</Text>
                <View style={styles.quantityContainer}>
                    <TouchableOpacity onPress={() => setQuantity(Math.max(1, quantity - 1))} style={styles.qtyBtn}>
                        <Text style={styles.qtyBtnText}>-</Text>
                    </TouchableOpacity>
                    <Text style={styles.qtyText}>{quantity}</Text>
                    <TouchableOpacity onPress={() => setQuantity(quantity + 1)} style={styles.qtyBtn}>
                        <Text style={styles.qtyBtnText}>+</Text>
                    </TouchableOpacity>
                </View>

                <Button
                    title="Add to Cart"
                    onPress={handleAddToCart}
                    loading={loading}
                    style={styles.addToCartButton}
                    icon={<ShoppingCart color={COLORS.white} size={20} style={{ marginRight: 8 }} />}
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
    image: {
        width: '100%',
        height: 300,
        backgroundColor: COLORS.white,
    },
    detailsContainer: {
        padding: SIZES.large,
        backgroundColor: COLORS.white,
        borderTopLeftRadius: SIZES.xlarge,
        borderTopRightRadius: SIZES.xlarge,
        marginTop: -20, // Overlap image slightly
        ...SHADOWS.medium,
        flex: 1,
        minHeight: 500,
    },
    headerRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: SIZES.small,
    },
    name: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.text,
        flex: 1,
    },
    price: {
        fontSize: 22,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    ratingRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: SIZES.medium,
    },
    ratingText: {
        marginLeft: 4,
        color: COLORS.gray,
        fontSize: 14,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: COLORS.text,
        marginTop: SIZES.medium,
        marginBottom: SIZES.small,
    },
    description: {
        fontSize: 16,
        color: COLORS.gray,
        lineHeight: 24,
    },
    quantityContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: SIZES.xlarge,
        marginTop: SIZES.small,
    },
    qtyBtn: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: COLORS.tertiary,
        alignItems: 'center',
        justifyContent: 'center',
    },
    qtyBtnText: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    qtyText: {
        fontSize: 18,
        fontWeight: 'bold',
        marginHorizontal: SIZES.large,
    },
    addToCartButton: {
        marginTop: SIZES.medium,
    }
});

export default ProductDetailsScreen;
