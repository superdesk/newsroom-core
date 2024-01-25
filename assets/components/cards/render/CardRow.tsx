import React from 'react';
import MoreNewsButton, {MoreNewsSearchKind} from './MoreNewsButton';
import {connect} from 'react-redux';
import {IProduct} from 'interfaces/product';

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
    companyProducts: Array<IProduct>;
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
            const isProductInUserProducts = userProducts.some(userProduct => userProduct._id === product._id);
            const isProductInCompanyProductsWithoutSeats = companyProducts.some(
                companyProduct => companyProduct._id === product._id && !companyProduct.seats
            );
            moreNews = isProductInUserProducts || isProductInCompanyProductsWithoutSeats;
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
    companyProducts: state.companyProducts,
});

const component: React.ComponentType<IOwnProps> = connect<IReduxStateProps, {}, IOwnProps>(mapStateToProps)(CardRow);

export default component;
