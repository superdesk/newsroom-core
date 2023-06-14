import React from 'react';
import PropTypes from 'prop-types';
import MoreNewsButton from './MoreNewsButton';
import {connect} from 'react-redux';

class CardRow extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        if (this.props.isActive) {
            this.cardElem.scrollIntoView({behavior: 'instant', block: 'end', inline: 'nearest'});
        }
    }
    render() {
        const {title, product, children, userProducts, userType, companyProducts} = this.props;
        let moreNews = this.props.moreNews;

        if (userType !== 'administrator') {
            const isProductInUserProducts = userProducts.some(userProduct => userProduct._id === product._id);
            const isProductInCompanyProductsWithoutSeats = companyProducts.some(
                companyProduct => companyProduct._id === product._id && !companyProduct.seats
            );
            moreNews = isProductInUserProducts || isProductInCompanyProductsWithoutSeats;
        }

        return (
            <div className='row' ref={(elem) => (this.cardElem = elem)}>
                <MoreNewsButton title={title} product={product} moreNews = {moreNews}/>
                {children}
            </div>
        );
    }
}

CardRow.propTypes = {
    title: PropTypes.string,
    product: PropTypes.object,
    isActive: PropTypes.bool,
    children: PropTypes.node.isRequired,
    moreNews: PropTypes.bool,
    user: PropTypes.object,
    userProducts: PropTypes.array,
    userType: PropTypes.string,
    companyProducts: PropTypes.array,
};

const mapStateToProps = (state) =>  ({
    userProducts: state.userProducts,
    userType: state.userType,
    companyProducts: state.companyProducts,
});

CardRow.defaultProps = {
    moreNews: true
};

export default connect(mapStateToProps)(CardRow);
