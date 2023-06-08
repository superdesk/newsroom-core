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
        const {title, product, children, userProducts,userType} = this.props;
        let moreNews = this.props.moreNews;
        if (userType !== 'administrator'){
            moreNews = userProducts.some((userProduct) => userProduct._id === product._id);
        }

        return (
            <div className='row' ref={(elem) => (this.cardElem = elem)}>
                {moreNews && <MoreNewsButton title={title} product={product} />}
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
};

const mapStateToProps = (state) =>  ({
    userProducts: state.userProducts,
    userType: state.userType,
});

CardRow.defaultProps = {
    moreNews: true
};

export default connect(mapStateToProps)(CardRow);
