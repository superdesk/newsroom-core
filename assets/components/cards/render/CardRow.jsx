import React from 'react';
import PropTypes from 'prop-types';
import MoreNewsButton from './MoreNewsButton';
import {connect} from 'react-redux';
import {userSelector} from '../../../user-profile/selectors';
import server from 'server';
import {isUserAdmin} from '../../../users/utils';

class CardRow extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: {}
        };
    }

    componentDidMount() {
        if (this.props.isActive) {
            this.cardElem.scrollIntoView({behavior: 'instant', block: 'end', inline: 'nearest'});
        }

        this.fetchUserData();
    }

    fetchUserData() {
        server
            .get(`/users/${this.props.user}`)
            .then((response) => {
                const user = response;
                this.setState({user: user});
            })
            .catch((error) => {
                console.error(error);
            });
    }

    render() {
        const {user} = this.state;
        const {title, product, children} = this.props;
        let moreNews = this.props.moreNews;

        if (Object.keys(user).length && !isUserAdmin(user)) {
            if (user.products.length === 0) {
                moreNews = false;
            } else {
                moreNews = user.products.some((userProduct) => userProduct._id === product._id);
            }
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
};

const mapStateToProps = (state) => ({
    user: userSelector(state),
});

CardRow.defaultProps = {
    moreNews: true
};

export default connect(mapStateToProps)(CardRow);
