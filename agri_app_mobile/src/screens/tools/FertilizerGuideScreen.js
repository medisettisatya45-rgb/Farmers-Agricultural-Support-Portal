
import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';

const FertilizerGuideScreen = () => {
    // Ideally this data comes from an API or local JSON
    const crops = [
        { name: 'Wheat', fertilizer: 'Urea, DAP', dose: '100kg/ha Urea, 50kg/ha DAP' },
        { name: 'Rice', fertilizer: 'Urea, SSP, MOP', dose: '120kg/ha Urea, 60kg/ha SSP' },
        { name: 'Cotton', fertilizer: 'DAP, MOP', dose: '80kg/ha DAP' },
    ];

    return (
        <ScrollView style={styles.container}>
            <Text style={styles.title}>Fertilizer Guide</Text>
            <Text style={styles.subtitle}>Recommendations for optimal crop growth.</Text>

            {crops.map((crop, index) => (
                <View key={index} style={styles.card}>
                    <Text style={styles.cropName}>{crop.name}</Text>
                    <View style={styles.row}>
                        <Text style={styles.label}>Fertilizers:</Text>
                        <Text style={styles.value}>{crop.fertilizer}</Text>
                    </View>
                    <View style={styles.row}>
                        <Text style={styles.label}>Dosage:</Text>
                        <Text style={styles.value}>{crop.dose}</Text>
                    </View>
                </View>
            ))}
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
        marginBottom: SIZES.large,
    },
    card: {
        backgroundColor: COLORS.white,
        padding: SIZES.medium,
        borderRadius: SIZES.radius,
        marginBottom: SIZES.medium,
        ...SHADOWS.small,
    },
    cropName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: SIZES.small,
    },
    row: {
        flexDirection: 'row',
        marginBottom: 4,
    },
    label: {
        fontWeight: '600',
        width: 100,
        color: COLORS.gray,
    },
    value: {
        flex: 1,
        color: COLORS.dark,
    }
});

export default FertilizerGuideScreen;
