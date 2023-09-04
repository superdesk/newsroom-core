import React from 'react';
import MoreNewsButton, {MoreNewsSearchKind} from './MoreNewsButton';
import {connect} from 'react-redux';

interface IOwnProps {
    id: string;
    title: string;
    children: any;
    isActive?: boolean;
    moreNews?: boolean;
    user?: any;
    kind?: MoreNewsSearchKind;
}

interface IReduxStateProps {
    userProducts: Array<any>;
    userType: string;
}

type IComponentProps = IOwnProps & IReduxStateProps

class CardRow extends React.Component<IComponentProps, any> {
    cardElem: any;

    constructor(props: any) {
        super(props);
    }

    componentDidMount() {
        if (this.props.isActive) {
            this.cardElem.scrollIntoView({behavior: 'instant', block: 'end', inline: 'nearest'});
        }
    }

    render() {
        const {title, id, children, userProducts, userType, kind} = this.props;
        let moreNews = this.props.moreNews == null ? true : this.props.moreNews;

        if (userType !== 'administrator' && kind == null) {
            moreNews = userProducts.some((userProduct: any) => userProduct._id === id);
        }

        return (
            <div className='row' ref={(elem) => (this.cardElem = elem)}>
                <MoreNewsButton title={title} id={id} kind={kind ?? 'product'} moreNews={moreNews} />
                {children}
            </div>
        );
    }
}

const mapStateToProps = (state: any): IReduxStateProps => ({
    userProducts: state.userProducts,
    userType: state.userType,
});

const component: React.ComponentType<IOwnProps> = connect<IReduxStateProps, {}, IOwnProps>(mapStateToProps)(CardRow);

export default component;
