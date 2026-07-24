import React from 'react';

interface IProps {
    fallback?: React.ReactNode;
    label?: string;
}

interface IState {
    error: boolean;
}

/**
 * Contains a render error, so it doesn't unmount everything around it.
 */
export class ErrorBoundary extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);
        this.state = {error: false};
    }

    static getDerivedStateFromError(): IState {
        return {error: true};
    }

    componentDidCatch(error: any, info: any) {
        console.error(`Error in ${this.props.label || 'component'}`, error, info);
    }

    render() {
        if (this.state.error) {
            return this.props.fallback ?? null;
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
