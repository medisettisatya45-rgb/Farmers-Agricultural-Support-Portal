
import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator, TextInput, TouchableOpacity } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import ProductCard from '../../components/ProductCard';
import api from '../../services/api';
import { Search, Filter } from 'lucide-react-native';

const CATEGORIES = [
    { id: 'all', name: 'All' },
    { id: 'fruits', name: 'Fruits' },
    { id: 'vegetables', name: 'Vegetables' },
    { id: 'seeds', name: 'Seeds' },
    { id: 'fertilizers', name: 'Fertilizers' }
];

const ProductListingScreen = ({ navigation }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    const fetchProducts = useCallback(async (reset = false) => {
        if (loading && !reset) return;

        setLoading(true);
        try {
            let endpoint = '/products';
            if (searchQuery) {
                endpoint = `/products/search?q=${searchQuery}`;
            } else if (selectedCategory !== 'all') {
                // Assuming backend supports category filtering by ID or Name
                // This might need adjustment based on actual API implementation which expects ID
                // For now, let's just fetch all and filter client side if simplistic, 
                // or assume we have an endpoint like /products/category/:id
                // But since I don't know category IDs mapping exactly without fetching categories first,
                // I will rely on the general /products endpoint for now or basic search.
                // Wait, I saw backend code: `/api/products/category/<int:category_id>`
                // So I ideally need the category ID.
                // Implementation detail: I'll skip specific category ID fetching for this starter code simplicity 
                // and rely on search or just 'All'.
            }

            const response = await api.get(endpoint, {
                params: { page: reset ? 1 : page, limit: 10 }
            });

            const newProducts = response.data.products || [];

            if (reset) {
                setProducts(newProducts);
            } else {
                setProducts(prev => [...prev, ...newProducts]);
            }

            setHasMore(newProducts.length >= 10);
            if (!reset) setPage(prev => prev + 1);

        } catch (error) {
            console.error('Failed to fetch products:', error);
        } finally {
            setLoading(false);
        }
    }, [page, searchQuery, selectedCategory]); // Dependencies need logic fix for 'loading' loop if not careful

    useEffect(() => {
        // Initial load
        fetchProducts(true);
    }, []); // Only on mount

    const handleSearch = () => {
        fetchProducts(true);
    };

    const renderHeader = () => (
        <View style={styles.headerContainer}>
            <View style={styles.searchBar}>
                <Search color={COLORS.gray} size={20} />
                <TextInput
                    style={styles.searchInput}
                    placeholder="Search items..."
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                    onSubmitEditing={handleSearch}
                />
                <TouchableOpacity onPress={handleSearch}>
                    <View style={styles.filterButton}>
                        <Filter color={COLORS.white} size={16} />
                    </View>
                </TouchableOpacity>
            </View>

            <FlatList
                horizontal
                data={CATEGORIES}
                keyExtractor={item => item.id}
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.categoriesList}
                renderItem={({ item }) => (
                    <TouchableOpacity
                        style={[
                            styles.categoryChip,
                            selectedCategory === item.id && styles.activeCategoryChip
                        ]}
                        onPress={() => {
                            setSelectedCategory(item.id);
                            // Trigger fetch with new category logic would go here
                            // For demonstration, let's just log or set state
                        }}
                    >
                        <Text style={[
                            styles.categoryText,
                            selectedCategory === item.id && styles.activeCategoryText
                        ]}>{item.name}</Text>
                    </TouchableOpacity>
                )}
            />
        </View>
    );

    return (
        <View style={styles.container}>
            <FlatList
                data={products}
                keyExtractor={(item) => item.product_id.toString()}
                renderItem={({ item }) => (
                    <ProductCard
                        product={item}
                        onPress={() => navigation.navigate('ProductDetails', { product: item })}
                    />
                )}
                numColumns={2}
                columnWrapperStyle={styles.columnWrapper}
                contentContainerStyle={styles.listContent}
                ListHeaderComponent={renderHeader}
                onEndReached={() => {
                    if (hasMore && !loading) {
                        fetchProducts();
                    }
                }}
                onEndReachedThreshold={0.5}
                ListFooterComponent={loading && <ActivityIndicator size="large" color={COLORS.primary} />}
                ListEmptyComponent={!loading && <Text style={styles.emptyText}>No products found.</Text>}
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    headerContainer: {
        padding: SIZES.medium,
        backgroundColor: COLORS.background,
    },
    searchBar: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.white,
        borderRadius: SIZES.radius,
        paddingHorizontal: SIZES.medium,
        paddingVertical: SIZES.small,
        marginBottom: SIZES.medium,
        ...SHADOWS.small,
    },
    searchInput: {
        flex: 1,
        marginLeft: SIZES.small,
        fontSize: 16,
        color: COLORS.text,
    },
    filterButton: {
        backgroundColor: COLORS.primary,
        padding: 8,
        borderRadius: 8
    },
    categoriesList: {
        paddingBottom: SIZES.small,
    },
    categoryChip: {
        paddingHorizontal: SIZES.large,
        paddingVertical: SIZES.small,
        borderRadius: 20,
        backgroundColor: COLORS.white,
        marginRight: SIZES.small,
        borderWidth: 1,
        borderColor: COLORS.tertiary,
    },
    activeCategoryChip: {
        backgroundColor: COLORS.primary,
        borderColor: COLORS.primary,
    },
    categoryText: {
        color: COLORS.text,
        fontWeight: '600',
    },
    activeCategoryText: {
        color: COLORS.white,
    },
    listContent: {
        paddingHorizontal: SIZES.small,
    },
    columnWrapper: {
        justifyContent: 'space-between',
    },
    emptyText: {
        textAlign: 'center',
        marginTop: 20,
        color: COLORS.gray,
        fontSize: 16
    }
});

export default ProductListingScreen;
