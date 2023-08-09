import React from 'react';
import PropTypes from 'prop-types';
import MoreNewsButton from './MoreNewsButton';
import {connect} from 'react-redux';

class CardRow extends React.Component<any, any> {
    static propTypes: any;
    static defaultProps: any;
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
        const {title, productId, children, userProducts,userType} = this.props;
        let moreNews = this.props.moreNews;
        if (userType !== 'administrator'){
            moreNews = userProducts.some((userProduct: any) => userProduct._id === productId);
        }

        return (
            <div className='row' ref={(elem) => (this.cardElem = elem)}>
                <MoreNewsButton title={title} productId={productId} moreNews = {moreNews}/>
                {children}
            </div>
        );
    }
}

CardRow.propTypes = {
    title: PropTypes.string,
    productId: PropTypes.string,
    isActive: PropTypes.bool,
    children: PropTypes.node.isRequired,
    moreNews: PropTypes.bool,
    user: PropTypes.object,
    userProducts: PropTypes.array,
    userType: PropTypes.string,
};

const mapStateToProps = (state: any) =>  ({
    userProducts: state.userProducts,
    userType: state.userType,
});

CardRow.defaultProps = {
    moreNews: true
};


const component: React.ComponentType<any> = connect(mapStateToProps)(CardRow);

export default component;
