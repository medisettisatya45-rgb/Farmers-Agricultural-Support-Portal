
import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking } from 'react-native';
import { COLORS, SIZES, SHADOWS } from '../../constants/theme';
import { FileText, ChevronRight, Bookmark } from 'lucide-react-native';

const schemes = [
    {
        id: 1,
        title: 'PM Kisan Samman Nidhi',
        description: 'Financial support of ₹6,000 per year to all landholding farmer families.',
        link: 'https://pmkisan.gov.in/'
    },
    {
        id: 2,
        title: 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
        description: 'Crop insurance scheme to provide financial support in case of crop failure.',
        link: 'https://pmfby.gov.in/'
    },
    {
        id: 3,
        title: 'Soil Health Card Scheme',
        description: 'Provides information on soil health to farmers to help them use optimal fertilizers.',
        link: 'https://soilhealth.dac.gov.in/'
    },
    {
        id: 4,
        title: 'Kisan Credit Card (KCC)',
        description: 'Provides affordable credit to farmers for agriculture and allied activities.',
        link: 'https://www.myscheme.gov.in/schemes/kcc'
    },
    {
        id: 5,
        title: 'e-NAM (National Agriculture Market)',
        description: 'Online trading platform for agricultural commodities in India.',
        link: 'https://www.enam.gov.in/'
    }
];

const GovernmentSchemesScreen = () => {
    const openLink = (url) => {
        Linking.openURL(url).catch(err => console.error("Couldn't load page", err));
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Government Schemes</Text>
                <Text style={styles.subtitle}>Explore financial aid and support programs for farmers.</Text>
            </View>

            <View style={styles.list}>
                {schemes.map((scheme) => (
                    <TouchableOpacity key={scheme.id} style={styles.card} onPress={() => openLink(scheme.link)}>
                        <View style={styles.cardContent}>
                            <View style={styles.iconBox}>
                                <FileText color={COLORS.primary} size={24} />
                            </View>
                            <View style={styles.textContainer}>
                                <Text style={styles.cardTitle}>{scheme.title}</Text>
                                <Text style={styles.cardDesc}>{scheme.description}</Text>
                            </View>
                            <ChevronRight color={COLORS.gray} size={20} />
                        </View>
                    </TouchableOpacity>
                ))}
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
        padding: SIZES.large,
        backgroundColor: COLORS.white,
        marginBottom: SIZES.medium,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: SIZES.small,
    },
    subtitle: {
        fontSize: 14,
        color: COLORS.gray,
    },
    list: {
        paddingHorizontal: SIZES.medium,
        paddingBottom: SIZES.large,
    },
    card: {
        backgroundColor: COLORS.white,
        borderRadius: SIZES.radius,
        marginBottom: SIZES.medium,
        padding: SIZES.medium,
        ...SHADOWS.small,
    },
    cardContent: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    iconBox: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: COLORS.tertiary,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: SIZES.medium,
    },
    textContainer: {
        flex: 1,
        marginRight: SIZES.small,
    },
    cardTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 4,
    },
    cardDesc: {
        fontSize: 13,
        color: COLORS.gray,
        lineHeight: 18,
    }
});

export default GovernmentSchemesScreen;
