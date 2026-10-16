
import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert, Platform } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import Button from '../../components/Button';
import Input from '../../components/Input';
import api from '../../services/api';

const SellProductScreen = ({ navigation }) => {
    const [name, setName] = useState('');
    const [price, setPrice] = useState('');
    const [quantity, setQuantity] = useState('');
    const [category, setCategory] = useState('');
    const [description, setDescription] = useState('');
    const [imageUrl, setImageUrl] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        if (!name || !price || !category) {
            Alert.alert('Error', 'Please fill all required fields');
            return;
        }

        setLoading(true);
        try {
            // In a real app, you would upload the image first to an endpoint
            // and get the URL back.
            // Here we assume imageUrl is provided directly or handled.

            const productData = {
                name,
                price: parseFloat(price),
                stock_quantity: parseInt(quantity) || 0,
                category, // This should probably be an ID in production
                category_id: 1, // Mock ID for demo
                description,
                image_url: imageUrl || 'https://via.placeholder.com/300'
            };

            await api.post('/products', productData);

            Alert.alert('Success', 'Product Listed Successfully!');
            navigation.goBack();
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'Could not list product. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <ScrollView style={styles.container}>
            <Text style={styles.title}>Sell Your Produce</Text>
            <Text style={styles.subtitle}>List your crops/products for buyers.</Text>

            <View style={styles.form}>
                <Input
                    label="Product Name *"
                    placeholder="e.g. Fresh Tomatoes"
                    value={name}
                    onChangeText={setName}
                />

                <View style={styles.row}>
                    <View style={{ flex: 1, marginRight: 8 }}>
                        <Input
                            label="Price (₹/kg) *"
                            placeholder="e.g. 40"
                            value={price}
                            onChangeText={setPrice}
                            keyboardType="numeric"
                        />
                    </View>
                    <View style={{ flex: 1, marginLeft: 8 }}>
                        <Input
                            label="Quantity (kg)"
                            placeholder="e.g. 100"
                            value={quantity}
                            onChangeText={setQuantity}
                            keyboardType="numeric"
                        />
                    </View>
                </View>

                <Input
                    label="Category *"
                    placeholder="e.g. Vegetables, Fruits, Grains"
                    value={category}
                    onChangeText={setCategory}
                />

                <Input
                    label="Description"
                    placeholder="Describe your produce..."
                    value={description}
                    onChangeText={setDescription}
                    multiline
                    numberOfLines={4}
                />

                <Input
                    label="Image URL"
                    placeholder="https://example.com/image.jpg"
                    value={imageUrl}
                    onChangeText={setImageUrl}
                />

                <Button
                    title={loading ? "Listing..." : "List Product"}
                    onPress={handleSubmit}
                    disabled={loading}
                    style={{ marginTop: 20 }}
                />
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
        padding: SIZES.medium,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginBottom: SIZES.small,
    },
    subtitle: {
        fontSize: 16,
        color: COLORS.gray,
        marginBottom: SIZES.large
    },
    form: {
        marginBottom: 40,
        backgroundColor: COLORS.white,
        padding: SIZES.large,
        borderRadius: SIZES.radius,
        ...SHADOWS.small,
    },
    row: {
        flexDirection: 'row',
    }
});

export default SellProductScreen;
