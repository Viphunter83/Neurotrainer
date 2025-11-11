/**
 * LoginScreen.tsx
 *
 * Экран входа с email/password валидацией и error handling.
 * Features:
 * - Real-time field validation
 * - Loading state management
 * - Error message display
 * - "Remember me" option (future)
 * - Link to registration
 */

import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Text,
  SafeAreaView,
  Keyboard,
  Animated,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { loginUser, clearError } from '../../store/slices/authSlice';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  BORDER_RADIUS,
  SHADOWS,
} from '../../styles/theme';
import { validateEmail, validatePassword } from '../../utils/validators';

interface FormErrors {
  email?: string;
  password?: string;
}

interface FormValues {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface LoginScreenProps {
  navigation: any;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ navigation }) => {
  const dispatch = useAppDispatch();
  const { isLoading, error } = useAppSelector((state) => state.auth);

  // Form state
  const [formValues, setFormValues] = useState<FormValues>({
    email: '',
    password: '',
    rememberMe: false,
  });
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Animations
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  // Validation logic
  const validateField = useCallback(
    (field: string, value: string): string | undefined => {
      switch (field) {
        case 'email':
          return validateEmail(value) ? undefined : 'Invalid email address';
        case 'password':
          return validatePassword(value)
            ? undefined
            : 'Password must be at least 8 characters and contain uppercase, lowercase, digit, and special character';
        default:
          return undefined;
      }
    },
    [],
  );

  // Handle field change
  const handleFieldChange = useCallback(
    (field: keyof FormValues, value: any) => {
      setFormValues((prev) => ({ ...prev, [field]: value }));
      // Real-time validation for touched fields
      if (touched[field]) {
        const error = validateField(field, value);
        setFormErrors((prev) => ({ ...prev, [field]: error }));
      }
    },
    [touched, validateField],
  );

  // Handle field blur
  const handleFieldBlur = useCallback(
    (field: string) => {
      setTouched((prev) => ({ ...prev, [field]: true }));
      const error = validateField(
        field,
        formValues[field as keyof FormValues] as string,
      );
      setFormErrors((prev) => ({ ...prev, [field]: error }));
    },
    [formValues, validateField],
  );

  // Check if form is valid
  const isFormValid = useMemo(() => {
    return (
      validateEmail(formValues.email) &&
      validatePassword(formValues.password) &&
      !isLoading &&
      Object.keys(formErrors).length === 0
    );
  }, [formValues, formErrors, isLoading]);

  // Handle login
  const handleLogin = useCallback(async () => {
    // Validate all fields before submission
    const newErrors: FormErrors = {};
    if (!validateEmail(formValues.email)) {
      newErrors.email = 'Invalid email address';
    }
    if (!validatePassword(formValues.password)) {
      newErrors.password = 'Invalid password';
    }

    if (Object.keys(newErrors).length > 0) {
      setFormErrors(newErrors);
      setTouched({ email: true, password: true });
      return;
    }

    // Submit
    const result = await dispatch(
      loginUser({
        email: formValues.email,
        password: formValues.password,
      }),
    );

    if (result.type === 'auth/login/fulfilled') {
      // Success - navigation handled by Redux or RootNavigator
    }
  }, [formValues, dispatch]);

  // Navigate to register
  const handleNavigateToRegister = useCallback(() => {
    Keyboard.dismiss();
    navigation.replace('Register');
  }, [navigation]);

  // Clear error when component mounts
  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  // Animation on mount
  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, slideAnim]);

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <Animated.View
            style={[
              styles.content,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            {/* Header */}
            <View style={styles.header}>
              <Text style={styles.title}>Welcome Back</Text>
              <Text style={styles.subtitle}>
                Sign in to continue your fitness journey
              </Text>
            </View>

            {/* Error Alert */}
            {error && (
              <View style={styles.errorAlert}>
                <Text style={styles.errorAlertText}>⚠️ {error}</Text>
              </View>
            )}

            {/* Form */}
            <View style={styles.form}>
              {/* Email Input */}
              <Input
                label="Email Address"
                placeholder="you@example.com"
                value={formValues.email}
                onChangeText={(value) => handleFieldChange('email', value)}
                onBlur={() => handleFieldBlur('email')}
                keyboardType="email-address"
                error={touched.email ? formErrors.email : undefined}
                editable={!isLoading}
              />

              {/* Password Input */}
              <Input
                label="Password"
                placeholder="Enter your password"
                value={formValues.password}
                onChangeText={(value) => handleFieldChange('password', value)}
                onBlur={() => handleFieldBlur('password')}
                secureTextEntry
                error={touched.password ? formErrors.password : undefined}
                style={{ marginTop: SPACING.md }}
                editable={!isLoading}
              />

              {/* Remember Me */}
              <TouchableOpacity
                style={styles.rememberMeContainer}
                onPress={() =>
                  handleFieldChange('rememberMe', !formValues.rememberMe)
                }
              >
                <View
                  style={[
                    styles.checkbox,
                    formValues.rememberMe && styles.checkboxChecked,
                  ]}
                >
                  {formValues.rememberMe && (
                    <Text style={styles.checkmark}>✓</Text>
                  )}
                </View>
                <Text style={styles.rememberMeText}>Remember me</Text>
              </TouchableOpacity>

              {/* Login Button */}
              <Button
                title="Sign In"
                onPress={handleLogin}
                disabled={!isFormValid}
                isLoading={isLoading}
                size="lg"
                style={{ marginTop: SPACING.lg }}
              />

              {/* Divider */}
              <View style={styles.divider}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>or</Text>
                <View style={styles.dividerLine} />
              </View>

              {/* Social Login (Future) */}
              <Button
                title="Continue with Google"
                onPress={() => {
                  // TODO: Implement Google Sign-In
                }}
                variant="outline"
                size="lg"
              />
            </View>

            {/* Register Link */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>Don't have an account? </Text>
              <TouchableOpacity onPress={handleNavigateToRegister}>
                <Text style={styles.footerLink}>Sign Up</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: SPACING.md,
  },
  content: {
    flex: 1,
    justifyContent: 'space-between',
    paddingVertical: SPACING.lg,
  },
  header: {
    marginTop: SPACING.xl,
    marginBottom: SPACING.xl,
  },
  title: {
    fontSize: TYPOGRAPHY.h2.size,
    fontWeight: TYPOGRAPHY.h2.weight,
    color: COLORS.text,
    marginBottom: SPACING.sm,
  },
  subtitle: {
    fontSize: TYPOGRAPHY.bodySmall.size,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
  errorAlert: {
    backgroundColor: COLORS.errorLight,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.error,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    marginBottom: SPACING.lg,
  },
  errorAlertText: {
    color: COLORS.error,
    fontSize: TYPOGRAPHY.body.size,
    fontWeight: '500',
  },
  form: {
    marginVertical: SPACING.lg,
  },
  rememberMeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SPACING.md,
    marginBottom: SPACING.md,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderWidth: 2,
    borderColor: COLORS.border,
    borderRadius: BORDER_RADIUS.sm,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.sm,
  },
  checkboxChecked: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  checkmark: {
    color: COLORS.white,
    fontSize: 14,
    fontWeight: 'bold',
  },
  rememberMeText: {
    fontSize: TYPOGRAPHY.body.size,
    color: COLORS.text,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: SPACING.lg,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: COLORS.border,
  },
  dividerText: {
    marginHorizontal: SPACING.md,
    color: COLORS.textSecondary,
    fontSize: TYPOGRAPHY.body.size,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: SPACING.lg,
    paddingBottom: SPACING.md,
  },
  footerText: {
    fontSize: TYPOGRAPHY.body.size,
    color: COLORS.textSecondary,
  },
  footerLink: {
    fontSize: TYPOGRAPHY.body.size,
    color: COLORS.primary,
    fontWeight: '600',
  },
});

export default LoginScreen;
