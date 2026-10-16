
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import Button from '../../components/Button';
import { Trash2 } from 'lucide-react-native';
import api from '../../services/api';

const CartScreen = ({ navigation }) => {
    const [cartItems, setCartItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [total, setTotal] = useState(0);

    const fetchCart = async () => {
        setLoading(true);
        try {
            const response = await api.get('/cart');
            if (response.data && response.data.items) {
                setCartItems(response.data.items);
                setTotal(response.data.total_amount);
            } else {
                setCartItems([]);
                setTotal(0);
            }
        } catch (error) {
            console.error(error);
            // Mock data for demo if API fails
            setCartItems([
                { product_id: 1, name: 'Fresh Tomatoes', price: 40, quantity: 2, subtotal: 80 },
                { product_id: 2, name: 'Wheat Seeds', price: 120, quantity: 1, subtotal: 120 },
            ]);
            setTotal(200);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCart();
    }, []);

    const handleCheckout = () => {
        Alert.alert('Checkout', `Total Amount: ₹${total}\n proceed to payment?`, [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Pay Now', onPress: () => Alert.alert('Success', 'Order Placed Successfully!') }
        ]);
    };

    if (loading) {
        return (
            <View style={styles.centered}>
                <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
        );
    }

    return (
        <View style={styles.container}>
            {cartItems.length === 0 ? (
                <View style={styles.emptyContainer}>
                    <Text style={styles.emptyText}>Your cart is empty.</Text>
                    <Button title="Shop Now" onPress={() => navigation.navigate('ProductListing')} style={{ marginTop: 20 }} />
                </View>
            ) : (
                <>
                    <FlatList
                        data={cartItems}
                        keyExtractor={(item) => item.product_id.toString()}
                        contentContainerStyle={styles.listContent}
                        renderItem={({ item }) => (
                            <View style={styles.cartItem}>
                                <View style={styles.itemInfo}>
                                    <Text style={styles.itemName}>{item.name}</Text>
                                    <Text style={styles.itemPrice}>₹{item.price} x {item.quantity} kg</Text>
                                </View>
                                <View style={styles.itemActions}>
                                    <Text style={styles.itemSubtotal}>₹{item.subtotal}</Text>
                                    <TouchableOpacity onPress={() => Alert.alert('Remove', 'Remove item from cart?')}>
                                        <Trash2 color={COLORS.error} size={20} style={{ marginLeft: 15 }} />
                                    </TouchableOpacity>
                                </View>
                            </View>
                        )}
                    />
                    <View style={styles.footer}>
                        <View style={styles.totalRow}>
                            <Text style={styles.totalLabel}>Total:</Text>
                            <Text style={styles.totalAmount}>₹{total}</Text>
                        </View>
                        <Button title="Checkout" onPress={handleCheckout} />
                    </View>
                </>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    centered: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center'
    },
    listContent: {
        padding: SIZES.medium,
    },
    cartItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: COLORS.white,
        padding: SIZES.medium,
        borderRadius: SIZES.radius,
        marginBottom: SIZES.small,
        ...SHADOWS.small,
    },
    itemInfo: {
        flex: 1,
    },
    itemName: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    itemPrice: {
        fontSize: 14,
        color: COLORS.gray,
        marginTop: 4,
    },
    itemActions: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    itemSubtotal: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    footer: {
        padding: SIZES.large,
        backgroundColor: COLORS.white,
        borderTopLeftRadius: SIZES.xlarge,
        borderTopRightRadius: SIZES.xlarge,
        ...SHADOWS.medium,
    },
    totalRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: SIZES.large,
    },
    totalLabel: {
        fontSize: 18,
        color: COLORS.text,
    },
    totalAmount: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    emptyText: {
        fontSize: 18,
        color: COLORS.gray,
    }

});

export default CartScreen;
