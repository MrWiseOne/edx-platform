import React from 'react';
import Modal from '@edx/paragon/src/Modal/index.jsx';
import Button from '@edx/paragon/src/Button/index.jsx';

import Carousel from './Carousel.jsx';

export class UpsellModal extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Modal
                className="upsell-modal"
                open
                title="Learning Insights"
                body={(
                     <Carousel id="upsell-modal" slides={this.props.slides} />
                )}
                buttons={[
                    <Button
                      label="Upgrade ($100 USD)"
                      display="Upgrade ($100 USD)"
                      buttonType="success"
                    />,
                ]}
                onClose={() => {}}
            />
        );
    }
}
